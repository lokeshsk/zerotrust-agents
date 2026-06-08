import httpx
import os
import asyncio

CONTROL_PLANE_URL = os.getenv("API_URL", "http://api:8001")

PRICING_MATRIX = {
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
    "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
    "default": {"prompt": 0.002, "completion": 0.002}
}

async def is_budget_exceeded(tenant_id: str, agent_id: str) -> bool:
    """
    Checks if the tenant's or agent's current spend has exceeded their monthly budget.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CONTROL_PLANE_URL}/policies/{tenant_id}/config", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                budget = data.get("monthly_budget", 0)
                spend = data.get("current_spend", 0)
                # Check tenant-level budget
                if budget > 0 and spend >= budget:
                    return True
                    
                # We could also check agent-level budget if the API returns it
                # For MVP we are keeping agent configs in the same payload or separate endpoint
                # Assuming /policies/{tenant_id}/agents/{agent_id}/config
                agent_resp = await client.get(f"{CONTROL_PLANE_URL}/policies/{tenant_id}/agents/{agent_id}", timeout=2.0)
                if agent_resp.status_code == 200:
                    agent_data = agent_resp.json()
                    agent_budget = agent_data.get("budget_limit", 0)
                    agent_spend = agent_data.get("current_spend", 0)
                    if agent_budget > 0 and agent_spend >= agent_budget:
                        return True
                        
    except Exception as e:
        print(f"Failed to check budget: {e}")
    return False

async def report_usage_async(tenant_id: str, agent_id: str, response_data: dict):
    """
    Extracts token usage from the upstream response and reports it to the Control Plane.
    Calculates cost based on the PRICING_MATRIX.
    """
    try:
        usage = response_data.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        model = response_data.get("model", "default")
        
        if total_tokens > 0:
            rates = PRICING_MATRIX.get(model)
            if not rates:
                for k, v in PRICING_MATRIX.items():
                    if k in model:
                        rates = v
                        break
            if not rates:
                rates = PRICING_MATRIX["default"]
                
            cost_dollars = (prompt_tokens / 1000.0) * rates["prompt"] + (completion_tokens / 1000.0) * rates["completion"]
            if cost_dollars == 0 and total_tokens > 0:
                 cost_dollars = (total_tokens / 1000.0) * rates["prompt"]
            
            async with httpx.AsyncClient() as client:
                await client.post(f"{CONTROL_PLANE_URL}/policies/{tenant_id}/usage", json={
                    "agent_id": agent_id,
                    "tokens": total_tokens,
                    "cost": cost_dollars
                }, timeout=2.0)
    except Exception as e:
        print(f"Failed to report usage: {e}")

def track_billing(tenant_id: str, agent_id: str, response_data: dict):
    """
    Fires off the asynchronous usage reporter.
    """
    asyncio.create_task(report_usage_async(tenant_id, agent_id, response_data))
