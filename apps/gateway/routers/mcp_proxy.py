import json
import logging
import asyncio
from fastapi import APIRouter, Request, HTTPException
from sse_starlette.sse import EventSourceResponse

from policy_engine import check_policy, log_tool_call
from routers.openai_proxy import semantic_dlp_check

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp", tags=["MCP Proxy"])

# A simple JSON-RPC 2.0 interceptor for MCP
# In a real deployment, the upstream MCP server URL would be configurable per-tenant.
UPSTREAM_MCP_URL = "http://localhost:8080"

async def process_mcp_message(message: dict, tenant_id: str, agent_id: str) -> dict:
    """
    Inspects an MCP JSON-RPC message. If it's a tools/call, evaluates policy.
    Returns the message to forward, or an error response if blocked.
    """
    method = message.get("method")
    
    if method == "tools/call":
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        arg_str = json.dumps(arguments)
        
        # Policy Check
        dlp_error = await semantic_dlp_check(arg_str, tenant_id)
        if dlp_error:
            is_allowed = False
            block_reason = dlp_error
        else:
            policy_action = await check_policy(tenant_id, agent_id, tool_name, arg_str)
            if policy_action == "allow":
                is_allowed = True
            elif policy_action == "require_approval":
                from policy_engine import create_pending_approval, wait_for_approval
                approval_id = await create_pending_approval(tenant_id, agent_id, tool_name, arg_str)
                if approval_id > 0:
                    logger.info(f"[{agent_id}] MCP tool {tool_name} requires approval. Suspending... (ID: {approval_id})")
                    is_allowed = await wait_for_approval(approval_id)
                else:
                    is_allowed = False
            else:
                is_allowed = False
                block_reason = f"SYSTEM FIREWALL BLOCK: Not authorized for '{tool_name}'."
                
        await log_tool_call(tenant_id, agent_id, tool_name, arg_str, is_allowed)
        
        if not is_allowed:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32000,
                    "message": block_reason
                }
            }
            
    return message

@router.post("/message")
async def mcp_message(request: Request):
    """
    Handles MCP SSE transport messages (HTTP POST to /message).
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    tenant_id = request.headers.get("x-tenant-id", "default")
    agent_id = request.headers.get("x-agent-id", "default-agent")
    
    processed = await process_mcp_message(body, tenant_id, agent_id)
    
    if "error" in processed and processed.get("id") == body.get("id"):
        # Blocked
        return processed
        
    # Forward to upstream
    from routers.openai_proxy import get_tenant_dlp_config
    config = await get_tenant_dlp_config(tenant_id)
    upstream_url = config.get("mcp_upstream_url", "http://localhost:8080") if config else "http://localhost:8080"
    
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{upstream_url}/message", json=processed, timeout=30.0)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32000, "message": f"Upstream MCP returned status {resp.status_code}"}}
    except Exception as e:
        logger.error(f"Failed to forward to MCP upstream: {e}")
        return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32000, "message": "Upstream MCP Unreachable"}}

@router.get("/sse")
async def mcp_sse(request: Request):
    """
    Handles MCP SSE transport connection.
    """
    async def sse_generator():
        yield {
            "event": "endpoint",
            "data": "/mcp/message"
        }
        while True:
            await asyncio.sleep(1)
            
    return EventSourceResponse(sse_generator())
    
# --- STDIO Transport ---
# Stdio is usually run via a CLI command, not FastAPI.
# We will provide a simple async loop that can be launched.
async def run_stdio_proxy(tenant_id="default", agent_id="default-agent"):
    import sys
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await loop.connect_write_pipe(lambda: asyncio.streams.FlowControlMixin(), sys.stdout)
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)
    
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            msg = json.loads(line.decode('utf-8'))
            processed = await process_mcp_message(msg, tenant_id, agent_id)
            
            # Here we would pipe `processed` to the REAL subprocess stdin
            # and read from its stdout to write back.
            # MVP: just echo blocked, or mock success
            if "error" in processed:
                writer.write((json.dumps(processed) + "\n").encode('utf-8'))
            else:
                resp = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"content": [{"type": "text", "text": "Upstream mocked"}]}}
                writer.write((json.dumps(resp) + "\n").encode('utf-8'))
            await writer.drain()
        except json.JSONDecodeError:
            pass
