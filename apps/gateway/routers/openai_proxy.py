from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import httpx
import litellm
import logging

logger = logging.getLogger(__name__)

from policy_engine import check_policy, log_tool_call
from proxy import forward_to_upstream

CONTROL_PLANE_URL = os.getenv("API_URL", "http://localhost:8001")

router = APIRouter(prefix="/v1", tags=["OpenAI Proxy"])

import re
import time
from prometheus_client import Counter, Histogram

# Prometheus Metrics
REQUEST_COUNT = Counter('gateway_requests_total', 'Total requests to the gateway', ['agent_id', 'status'])
TOOL_CALL_COUNT = Counter('gateway_tool_calls_total', 'Total tool calls intercepted', ['agent_id', 'tool_name', 'action'])
REQUEST_LATENCY = Histogram('gateway_request_latency_seconds', 'Request latency')

import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None

def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL)
    return redis_client

RATE_LIMIT_WINDOW_SEC = 10
MAX_CALLS_PER_WINDOW = 3

async def is_rate_limited(agent_id: str) -> bool:
    try:
        r = get_redis()
        now = time.time()
        key = f"rate_limit:{agent_id}"
        
        # Remove old entries
        await r.zremrangebyscore(key, 0, now - RATE_LIMIT_WINDOW_SEC)
        
        # Count requests in window
        count = await r.zcard(key)
        if count >= MAX_CALLS_PER_WINDOW:
            return True
            
        # Add this request
        await r.zadd(key, {str(now): now})
        # Set TTL to ensure keys don't live forever
        await r.expire(key, RATE_LIMIT_WINDOW_SEC)
        return False
    except Exception as e:
        print(f"Rate Limiter Error (falling open): {e}")
        return False
GATEWAY_SECRET = os.getenv("SECRET_KEY")
if not GATEWAY_SECRET:
    raise RuntimeError("SECRET_KEY environment variable is missing. It is required for security.")

async def get_tenant_dlp_config(tenant_id: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CONTROL_PLANE_URL}/policies/{tenant_id}/config", 
                headers={"x-gateway-secret": GATEWAY_SECRET},
                timeout=2.0
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch tenant config: {e}")
    return None

async def semantic_dlp_check(arguments: str, tenant_id: str) -> str:
    """
    Scans tool arguments for PII and destructive commands using a secondary LLM.
    Returns an error message if blocked, otherwise None.
    """
    if not arguments:
        return None
        
    config = await get_tenant_dlp_config(tenant_id)
    if config and config.get("dlp_model"):
        # Use LiteLLM to run the semantic check
        try:
            model = config["dlp_model"]
            api_base = config.get("dlp_api_base")
            api_key = config.get("dlp_api_key") or "dummy-key" # litellm might require a key even for local
            sensitivity = config.get("dlp_sensitivity", "high")

            sys_prompt = "You are a Zero Trust Security Analyzer. Your job is to inspect payloads sent to tools by AI agents. You must answer ONLY with 'BLOCK' or 'ALLOW'."
            
            if sensitivity == "high":
                user_prompt = f"Evaluate the following payload for ANY sensitive data (PII, SSN, Credit Cards, Internal IP addresses) OR destructive commands (DROP, DELETE, UPDATE without WHERE).\nPayload: {arguments}\nStrictly BLOCK if there is even a slight risk."
            elif sensitivity == "medium":
                user_prompt = f"Evaluate the following payload for clear PII (SSN, Credit Cards) or highly destructive commands (DROP TABLE, TRUNCATE).\nPayload: {arguments}\nBLOCK only if explicitly dangerous."
            else: # low
                user_prompt = f"Evaluate the following payload ONLY for highly destructive database operations (DROP TABLE, TRUNCATE). Ignore PII.\nPayload: {arguments}\nBLOCK only if it's clearly dropping a table."

            # Prepare kwargs for litellm
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "api_key": api_key,
                "max_tokens": 10
            }
            if api_base:
                kwargs["api_base"] = api_base
                
            response = await litellm.acompletion(**kwargs)
            content = response.choices[0].message.content.upper()
            
            if "BLOCK" in content:
                return f"Semantic DLP Block ({sensitivity} sensitivity): Malicious intent or sensitive data detected by LLM."
            return None
        except Exception as e:
            logger.error(f"LiteLLM DLP Check Failed, falling back to regex: {e}")

        
    # Fallback MVP regex check
    destructive_sql = re.compile(r'\b(DROP|DELETE|TRUNCATE|ALTER)\b', re.IGNORECASE)
    if destructive_sql.search(arguments):
        return "Semantic DLP Block: Destructive command detected in payload."
        
    ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    if ssn_pattern.search(arguments):
        return "Semantic DLP Block: Sensitive PII (SSN) detected in payload."
        
    return None

@router.post("/chat/completions")
async def chat_completions_proxy(request: Request):
    """
    A drop-in replacement for OpenAI's /v1/chat/completions.
    Intercepts traffic, routes via LiteLLM, evaluates policy, and logs.
    """
    start_time = time.time()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
        
    headers = dict(request.headers)
    agent_id = headers.get("x-agent-id", "default-agent")
    
    REQUEST_COUNT.labels(agent_id=agent_id, status="received").inc()
    
    # Authenticate the Agent via API Key
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return JSONResponse(status_code=401, content={
            "error": "Missing or invalid Authorization header. Must provide Bearer <API_KEY>"
        })
    api_key = auth_header.split(" ")[1]
    
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

    # 1. Anomaly Detection / Rate Limiting
    if await is_rate_limited(agent_id):
        REQUEST_COUNT.labels(agent_id=agent_id, status="rate_limited").inc()
        return JSONResponse(status_code=429, content={
            "error": f"Anomaly Detected: Agent '{agent_id}' exceeded rate limit."
        })

    # EE Features: Budget Checks
    # We check if the main.py EE_ACTIVE flag is set
    from main import EE_ACTIVE
    if EE_ACTIVE:
        from ee.billing import is_budget_exceeded, track_billing
        if await is_budget_exceeded(tenant_id, agent_id):
            REQUEST_COUNT.labels(agent_id=agent_id, status="budget_exceeded").inc()
            return JSONResponse(status_code=402, content={
                "error": f"Enterprise Billing Alert: Tenant '{tenant_id}' or Agent '{agent_id}' has exceeded their budget limit."
            })

    # Auto-Discovery: Intercept the 'tools' array in the payload and register them
    if "tools" in body:
        try:
            tool_names = [t.get("function", {}).get("name") for t in body["tools"] if t.get("type") == "function"]
            if tool_names:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{CONTROL_PLANE_URL}/policies/register", 
                        json={
                            "tenant_id": tenant_id,
                            "agent_id": agent_id,
                            "tools": tool_names
                        }, 
                        headers={"x-gateway-secret": GATEWAY_SECRET},
                        timeout=1.0
                    )
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")

    # 2. Forward request upstream via LiteLLM
    response_data = await forward_to_upstream(body)
    
    if body.get("stream", False):
        from fastapi.responses import StreamingResponse
        
        async def stream_generator():
            tool_call_buffers = {}
            from main import EE_ACTIVE
            
            try:
                async for chunk in response_data:
                    chunk_dict = chunk.model_dump()
                    choices = chunk_dict.get("choices", [])
                    if not choices:
                        yield f"data: {json.dumps(chunk_dict)}\n\n"
                        continue
                        
                    delta = choices[0].get("delta", {})
                    
                    if "tool_calls" in delta and delta["tool_calls"]:
                        for tc in delta["tool_calls"]:
                            idx = tc.get("index", 0)
                            if idx not in tool_call_buffers:
                                tool_call_buffers[idx] = {"id": tc.get("id"), "type": "function", "function": {"name": "", "arguments": ""}}
                            
                            func = tc.get("function", {})
                            if func.get("name"):
                                tool_call_buffers[idx]["function"]["name"] += func["name"]
                            if func.get("arguments"):
                                tool_call_buffers[idx]["function"]["arguments"] += func["arguments"]
                        continue
                    
                    # Yield normal text chunks
                    yield f"data: {json.dumps(chunk_dict)}\n\n"
                
                # Evaluate buffered tool calls
                if tool_call_buffers:
                    for idx, tc in tool_call_buffers.items():
                        tool_name = tc["function"]["name"]
                        arguments = tc["function"]["arguments"]
                        
                        dlp_error = await semantic_dlp_check(arguments, tenant_id)
                        block_reason = dlp_error
                        is_allowed = not bool(dlp_error)
                        
                        if is_allowed:
                            policy_action = await check_policy(tenant_id, agent_id, tool_name, arguments)
                            if policy_action == "allow":
                                is_allowed = True
                            elif policy_action == "require_approval":
                                from policy_engine import create_pending_approval, wait_for_approval
                                approval_id = await create_pending_approval(tenant_id, agent_id, tool_name, arguments)
                                if approval_id > 0:
                                    logger.info(f"[{agent_id}] Stream suspended for approval ID: {approval_id}")
                                    is_allowed = await wait_for_approval(approval_id)
                                else:
                                    is_allowed = False
                            else:
                                is_allowed = False
                                block_reason = f"SYSTEM FIREWALL BLOCK: You are not authorized to use the tool '{tool_name}'."
                        
                        await log_tool_call(tenant_id, agent_id, tool_name, arguments, is_allowed)
                        TOOL_CALL_COUNT.labels(agent_id=agent_id, tool_name=tool_name, action="allow" if is_allowed else "block").inc()
                        
                        if is_allowed:
                            # Send the whole tool call as one chunk
                            tc["index"] = idx
                            yield f"data: {json.dumps({'id': 'chunk', 'choices': [{'delta': {'tool_calls': [tc]}}]})}\n\n"
                        else:
                            # Send block message
                            msg_text = f"\n\n[{block_reason}]"
                            yield f"data: {json.dumps({'id': 'chunk', 'choices': [{'delta': {'content': msg_text}, 'finish_reason': 'stop'}]})}\n\n"
                
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Stream error: {e}")
                
        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    if EE_ACTIVE:
        track_billing(tenant_id, agent_id, response_data)

    # 3. Parse upstream response to see if the LLM wants to call a tool
    if "choices" in response_data and len(response_data["choices"]) > 0:
        message = response_data["choices"][0].get("message", {})
        
        # In LiteLLM/OpenAI standard format, tool calls look like this
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                
                # Semantic Payload Inspection (DLP)
                dlp_error = await semantic_dlp_check(arguments, tenant_id)
                
                if dlp_error:
                    is_allowed = False
                    block_reason = dlp_error
                else:
                    # Evaluate Policy Check
                    policy_action = await check_policy(tenant_id, agent_id, tool_name, arguments)
                    is_allowed = False
                    block_reason = f"SYSTEM FIREWALL BLOCK: You are not authorized to use the tool '{tool_name}'."
                    
                    if policy_action == "allow":
                        is_allowed = True
                    elif policy_action == "require_approval":
                        # HITL SUSPENSION LOGIC
                        from policy_engine import create_pending_approval, wait_for_approval
                        approval_id = await create_pending_approval(tenant_id, agent_id, tool_name, arguments)
                        if approval_id > 0:
                            # Suspend thread and wait for admin approval
                            logger.info(f"[{agent_id}] Tool {tool_name} requires approval. Suspending... (ID: {approval_id})")
                            is_allowed = await wait_for_approval(approval_id)
                            logger.info(f"[{agent_id}] Approval {approval_id} resolved: {'Allowed' if is_allowed else 'Denied'}")
                        else:
                            is_allowed = False # Fail closed if we couldn't create approval
                
                # Log the attempt
                await log_tool_call(tenant_id, agent_id, tool_name, arguments, is_allowed)
                TOOL_CALL_COUNT.labels(agent_id=agent_id, tool_name=tool_name, action="allow" if is_allowed else "block").inc()
                
                # If denied, block the tool call from reaching the Agent
                if not is_allowed:
                    response_data["choices"][0]["message"] = {
                        "role": "assistant",
                        "content": block_reason
                    }
                    if "tool_calls" in response_data["choices"][0]["message"]:
                        del response_data["choices"][0]["message"]["tool_calls"]
                    response_data["choices"][0]["finish_reason"] = "stop"
                    
    REQUEST_COUNT.labels(agent_id=agent_id, status="success").inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    return JSONResponse(content=response_data, status_code=200)
