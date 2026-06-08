from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import httpx
import time
import logging

from policy_engine import check_policy, log_tool_call
from routers.openai_proxy import (
    GATEWAY_SECRET, get_tenant_dlp_config, 
    semantic_dlp_check, is_rate_limited, REQUEST_COUNT, TOOL_CALL_COUNT, REQUEST_LATENCY
)
import os
CONTROL_PLANE_URL = os.getenv("API_URL", "http://localhost:8001")
import litellm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["Gemini Proxy"])

@router.post("/models/{model}:generateContent")
async def generate_content_proxy(model: str, request: Request):
    start_time = time.time()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    headers = dict(request.headers)
    agent_id = headers.get("x-agent-id", "default-agent")
    
    REQUEST_COUNT.labels(agent_id=agent_id, status="received").inc()
    
    # Authenticate (Gemini uses x-goog-api-key or query param key=...)
    api_key = headers.get("x-goog-api-key", "")
    if not api_key:
        api_key = request.query_params.get("key", "")
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
            tool_names = []
            for t in body["tools"]:
                for f in t.get("function_declarations", []):
                    if "name" in f:
                        tool_names.append(f["name"])
                        
            if tool_names:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{CONTROL_PLANE_URL}/policies/register", 
                        json={"tenant_id": tenant_id, "agent_id": agent_id, "tools": tool_names}, 
                        headers={"x-gateway-secret": GATEWAY_SECRET}, timeout=1.0
                    )
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")

    # Map to OpenAI format
    openai_tools = []
    if "tools" in body:
        for t in body["tools"]:
            for f in t.get("function_declarations", []):
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": f["name"],
                        "description": f.get("description", ""),
                        "parameters": f.get("parameters", {})
                    }
                })
    
    openai_messages = []
    for m in body.get("contents", []):
        role = m.get("role", "user")
        if role == "model":
            role = "assistant"
            
        parts = m.get("parts", [])
        text = " ".join([p.get("text", "") for p in parts if "text" in p])
        openai_messages.append({"role": role, "content": text})
        
    system_instruction = body.get("systemInstruction")
    if system_instruction:
        parts = system_instruction.get("parts", [])
        text = " ".join([p.get("text", "") for p in parts if "text" in p])
        if text:
            openai_messages.insert(0, {"role": "system", "content": text})

    litellm_kwargs = {
        "model": f"gemini/{model}",
        "messages": openai_messages,
    }
    if openai_tools:
        litellm_kwargs["tools"] = openai_tools

    if body.get("stream", False):
        litellm_kwargs["stream"] = True

    try:
        response = await litellm.acompletion(**litellm_kwargs)
        if body.get("stream", False):
            from fastapi.responses import StreamingResponse
            
            async def stream_generator():
                tool_call_buffers = {}
                from main import EE_ACTIVE
                
                try:
                    async for chunk in response:
                        chunk_dict = chunk.model_dump()
                        choices = chunk_dict.get("choices", [])
                        if not choices:
                            continue
                        
                        delta = choices[0].get("delta", {})
                        
                        if "tool_calls" in delta and delta["tool_calls"]:
                            for tc in delta["tool_calls"]:
                                idx = tc.get("index", 0)
                                if idx not in tool_call_buffers:
                                    tool_call_buffers[idx] = {"id": tc.get("id"), "type": "tool_use", "name": "", "input_str": ""}
                                
                                func = tc.get("function", {})
                                if func.get("name"):
                                    tool_call_buffers[idx]["name"] += func["name"]
                                if func.get("arguments"):
                                    tool_call_buffers[idx]["input_str"] += func["arguments"]
                            continue
                        
                        if "content" in delta and delta["content"]:
                            gemini_chunk = {
                                "candidates": [
                                    {
                                        "content": {
                                            "parts": [{"text": delta["content"]}],
                                            "role": "model"
                                        }
                                    }
                                ]
                            }
                            yield f'data: {json.dumps(gemini_chunk)}\n\n'

                    if tool_call_buffers:
                        for idx, tc in tool_call_buffers.items():
                            tool_name = tc["name"]
                            arguments = tc["input_str"]
                            
                            dlp_error = await semantic_dlp_check(arguments, tenant_id)
                            is_allowed = not bool(dlp_error)
                            block_reason = dlp_error
                            
                            if is_allowed:
                                policy_action = await check_policy(tenant_id, agent_id, tool_name, arguments)
                                if policy_action == "allow":
                                    is_allowed = True
                                elif policy_action == "require_approval":
                                    from policy_engine import create_pending_approval, wait_for_approval
                                    approval_id = await create_pending_approval(tenant_id, agent_id, tool_name, arguments)
                                    if approval_id > 0:
                                        is_allowed = await wait_for_approval(approval_id)
                                    else:
                                        is_allowed = False
                                else:
                                    is_allowed = False
                                    block_reason = f"SYSTEM FIREWALL BLOCK: Not authorized for '{tool_name}'."
                            
                            await log_tool_call(tenant_id, agent_id, tool_name, arguments, is_allowed)
                            TOOL_CALL_COUNT.labels(agent_id=agent_id, tool_name=tool_name, action="allow" if is_allowed else "block").inc()
                            
                            if is_allowed:
                                args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
                                gemini_chunk = {
                                    "candidates": [
                                        {
                                            "content": {
                                                "parts": [{"functionCall": {"name": tool_name, "args": args_dict}}],
                                                "role": "model"
                                            }
                                        }
                                    ]
                                }
                                yield f'data: {json.dumps(gemini_chunk)}\n\n'
                            else:
                                gemini_chunk = {
                                    "candidates": [
                                        {
                                            "content": {
                                                "parts": [{"text": f"\n\n[{block_reason}]"}],
                                                "role": "model"
                                            }
                                        }
                                    ]
                                }
                                yield f'data: {json.dumps(gemini_chunk)}\n\n'

                except Exception as e:
                    logger.error(f"Gemini stream error: {e}")
                    
            return StreamingResponse(stream_generator(), media_type="text/event-stream")

        response_data = response.model_dump()
    except Exception as e:
        logger.error(f"Gemini upstream error: {e}")
        return JSONResponse(status_code=502, content={"error": str(e)})

    if EE_ACTIVE:
        track_billing(tenant_id, response_data)

    # Reconstruct Gemini Response Format
    gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ]
    }
    
    if "choices" in response_data and response_data["choices"]:
        choice = response_data["choices"][0]
        msg = choice.get("message", {})
        
        if msg.get("content"):
            gemini_response["candidates"][0]["content"]["parts"].append({"text": msg["content"]})
            
        if "tool_calls" in msg and msg["tool_calls"]:
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
                    elif policy_action == "require_approval":
                        from policy_engine import create_pending_approval, wait_for_approval
                        approval_id = await create_pending_approval(tenant_id, agent_id, tool_name, arguments)
                        if approval_id > 0:
                            logger.info(f"[{agent_id}] Gemini tool {tool_name} requires approval. Suspending... (ID: {approval_id})")
                            is_allowed = await wait_for_approval(approval_id)
                        else:
                            is_allowed = False
                    else:
                        is_allowed = False
                        block_reason = f"SYSTEM FIREWALL BLOCK: Not authorized for '{tool_name}'."
                        
                await log_tool_call(tenant_id, agent_id, tool_name, arguments, is_allowed)
                
                if is_allowed:
                    args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
                    gemini_response["candidates"][0]["content"]["parts"].append({
                        "functionCall": {
                            "name": tool_name,
                            "args": args_dict
                        }
                    })
                else:
                    gemini_response["candidates"][0]["content"]["parts"].append({
                        "text": f"\n\n[{block_reason}]"
                    })

    REQUEST_COUNT.labels(agent_id=agent_id, status="success").inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return JSONResponse(content=gemini_response)
