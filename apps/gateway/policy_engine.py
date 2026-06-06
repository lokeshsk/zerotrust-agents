import httpx
import os

CONTROL_PLANE_URL = os.getenv("API_URL", "http://api:8001")
GATEWAY_SECRET = os.getenv("SECRET_KEY", "super-secret-firewall-key")

import json

async def check_policy(tenant_id: str, agent_id: str, tool_name: str, arguments: str) -> str:
    """
    Check with the control plane if the agent is allowed to call this tool.
    Returns "allow", "deny", or "require_approval".
    Evaluates JSON DSL rules if present.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CONTROL_PLANE_URL}/policies/{tenant_id}/{agent_id}/{tool_name}", 
                headers={"x-gateway-secret": GATEWAY_SECRET},
                timeout=2.0
            )
            if resp.status_code == 200:
                data = resp.json()
                action = data.get("action", "deny")
                dsl_rules_str = data.get("dsl_rules")
                
                # Evaluate DSL Rules if present
                if dsl_rules_str and action == "allow":
                    try:
                        rule = json.loads(dsl_rules_str)
                        args_dict = json.loads(arguments)
                        
                        field = rule.get("field")
                        operator = rule.get("operator")
                        expected_value = rule.get("value")
                        
                        if field in args_dict:
                            actual_value = args_dict[field]
                            if operator == "equals" and actual_value != expected_value:
                                return "deny"
                            elif operator == "not_equals" and actual_value == expected_value:
                                return "deny"
                    except Exception as e:
                        print(f"Failed to evaluate DSL rule: {e}")
                        return "deny" # Fail closed
                        
                return action
    except Exception as e:
        print(f"Policy Engine Error (failing closed): {e}")
    return "deny"

async def create_pending_approval(tenant_id: str, agent_id: str, tool_name: str, arguments: str) -> int:
    """
    Creates a pending approval request in the control plane and returns the approval ID.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{CONTROL_PLANE_URL}/policies/approvals", 
                json={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "arguments": arguments
                }, 
                headers={"x-gateway-secret": GATEWAY_SECRET},
                timeout=2.0
            )
            if resp.status_code == 200:
                return resp.json().get("id")
    except Exception as e:
        print(f"Error creating pending approval: {e}")
    return -1

async def wait_for_approval(approval_id: int) -> bool:
    """
    Polls the control plane until the approval is either 'approved' or 'rejected'.
    """
    import asyncio
    for _ in range(30): # Wait up to 60 seconds
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{CONTROL_PLANE_URL}/policies/approvals/{approval_id}", 
                    headers={"x-gateway-secret": GATEWAY_SECRET},
                    timeout=2.0
                )
                if resp.status_code == 200:
                    status = resp.json().get("status")
                    if status == "approved":
                        return True
                    elif status == "rejected":
                        return False
        except Exception:
            pass
        await asyncio.sleep(2)
    return False

async def log_tool_call(tenant_id: str, agent_id: str, tool_name: str, arguments: str, allowed: bool):
    """
    Asynchronously log the tool call to the Control Plane for auditing.
    """
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{CONTROL_PLANE_URL}/logs/", 
                json={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "allowed": allowed
                }, 
                headers={"x-gateway-secret": GATEWAY_SECRET},
                timeout=2.0
            )
    except:
        pass
