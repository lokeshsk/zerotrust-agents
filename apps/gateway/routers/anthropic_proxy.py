from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import httpx
import time
import logging

from policy_engine import check_policy, log_tool_call
from routers.openai_proxy import (
    CONTROL_PLANE_URL, GATEWAY_SECRET, get_tenant_dlp_config, 
    semantic_dlp_check, is_rate_limited, REQUEST_COUNT, TOOL_CALL_COUNT, REQUEST_LATENCY
)
import litellm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["Anthropic Proxy"])

@router.post("/messages")
async def messages_proxy(request: Request):
    start_time = time.time()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    headers = dict(request.headers)
    agent_id = headers.get("x-agent-id", "default-agent")
    
    REQUEST_COUNT.labels(agent_id=agent_id, status="received").inc()
    
    # Authenticate (Anthropic uses x-api-key usually, but we'll accept Authorization or x-api-key)
    api_key = headers.get("x-api-key", "")
    if not api_key:
        auth_header = headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            api_key = auth_header.split(" ")[1]
            
    if not api_key:
        return JSONResponse(status_code=401, content={"error": "Missing API Key"})
        
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CONTROL_PLANE_URL}/tenants/resolve-key?api_key={api_key}", 
                headers={"x-gateway-secret": GATEWAY_SECRET},
                timeout=2.0
            )
            if resp.status_code != 200:
                REQUEST_COUNT.labels(agent_id=agent_id, status="unauthorized").inc()
                return JSONResponse(status_code=401, content={"error": "Invalid API Key"})
            tenant_id = resp.json().get("tenant_id")
    except Exception as e:
        logger.error(f"Failed to resolve API key: {e}")
        return JSONResponse(status_code=500, content={"error": "Authentication service unavailable"})

    if await is_rate_limited(agent_id):
        REQUEST_COUNT.labels(agent_id=agent_id, status="rate_limited").inc()
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded."})

    from main import EE_ACTIVE
    if EE_ACTIVE:
        from ee.billing import is_budget_exceeded, track_billing
        if await is_budget_exceeded(tenant_id):
            return JSONResponse(status_code=402, content={"error": "Budget exceeded"})

    # Auto-discovery
    if "tools" in body:
        try:
            tool_names = [t.get("name") for t in body["tools"] if "name" in t]
            if tool_names:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{CONTROL_PLANE_URL}/policies/register", 
                        json={"tenant_id": tenant_id, "agent_id": agent_id, "tools": tool_names}, 
                        headers={"x-gateway-secret": GATEWAY_SECRET}, timeout=1.0
                    )
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")

    # Forward upstream. We just map Anthropic format to OpenAI format for litellm, then map back.
    # Litellm supports Anthropic messages natively? Actually, litellm.acompletion takes messages=[{"role": "user", "content": "..."}]
    
    # To keep it simple and robust, we pass the raw kwargs to litellm.
    # Litellm has `litellm.acompletion(..., **body)` but it expects OpenAI structure for tools!
    # So we must translate Anthropic tools to OpenAI tools.
    
    openai_tools = []
    if "tools" in body:
        for t in body["tools"]:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {})
                }
            })
    
    # Translate messages
    openai_messages = []
    if "system" in body:
        openai_messages.append({"role": "system", "content": body["system"]})
        
    for m in body.get("messages", []):
        openai_messages.append(m) # Usually compatible, except for tool_use content blocks
        
    # We will just pass the translated parts to litellm
    litellm_kwargs = {
        "model": body.get("model", "claude-3-haiku-20240307"),
        "messages": openai_messages,
    }
    if openai_tools:
        litellm_kwargs["tools"] = openai_tools
    if "max_tokens" in body:
        litellm_kwargs["max_tokens"] = body["max_tokens"]

    try:
        response = await litellm.acompletion(**litellm_kwargs)
        response_data = response.model_dump()
    except Exception as e:
        logger.error(f"Anthropic upstream error: {e}")
        return JSONResponse(status_code=502, content={"error": str(e)})

    if EE_ACTIVE:
        track_billing(tenant_id, response_data)

    # Reconstruct Anthropic Response Format
    anthropic_response = {
        "id": response_data.get("id", "msg_123"),
        "type": "message",
        "role": "assistant",
        "model": body.get("model"),
        "content": [],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": response_data.get("usage", {}).get("completion_tokens", 0)
        }
    }
    
    if "choices" in response_data and response_data["choices"]:
        choice = response_data["choices"][0]
        msg = choice.get("message", {})
        
        if msg.get("content"):
            anthropic_response["content"].append({
                "type": "text",
                "text": msg["content"]
            })
            
        if "tool_calls" in msg and msg["tool_calls"]:
            anthropic_response["stop_reason"] = "tool_use"
            for tc in msg["tool_calls"]:
                tool_name = tc["function"]["name"]
                arguments = tc["function"]["arguments"]
                
                # Policy check
                dlp_error = await semantic_dlp_check(arguments, tenant_id)
                if dlp_error:
                    is_allowed = False
                    block_reason = dlp_error
                else:
                    policy_action = await check_policy(tenant_id, agent_id, tool_name, arguments)
                    if policy_action == "allow":
                        is_allowed = True
                    else:
                        is_allowed = False
                        block_reason = f"SYSTEM FIREWALL BLOCK: Not authorized for '{tool_name}'."
                        
                await log_tool_call(tenant_id, agent_id, tool_name, arguments, is_allowed)
                
                if is_allowed:
                    anthropic_response["content"].append({
                        "type": "tool_use",
                        "id": tc.get("id"),
                        "name": tool_name,
                        "input": json.loads(arguments) if isinstance(arguments, str) else arguments
                    })
                else:
                    anthropic_response["content"].append({
                        "type": "text",
                        "text": f"\n\n[{block_reason}]"
                    })
                    anthropic_response["stop_reason"] = "end_turn"

    REQUEST_COUNT.labels(agent_id=agent_id, status="success").inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return JSONResponse(content=anthropic_response)
