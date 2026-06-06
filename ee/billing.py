import httpx
import os
import asyncio

CONTROL_PLANE_URL = os.getenv("API_URL", "http://api:8001")

async def is_budget_exceeded(tenant_id: str) -> bool:
    """
    Checks if the tenant's current spend has exceeded their monthly budget.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CONTROL_PLANE_URL}/policies/{tenant_id}/config", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                budget = data.get("monthly_budget", 0)
                spend = data.get("current_spend", 0)
                # If budget is 0, it means no limit.
                if budget > 0 and spend >= budget:
                    return True
    except Exception as e:
        print(f"Failed to check budget: {e}")
    return False

async def report_usage_async(tenant_id: str, response_data: dict):
    """
    Extracts token usage from the upstream response and reports it to the Control Plane.
    This assumes response_data follows OpenAI format: 
    { "usage": { "total_tokens": 150 } }
    """
    try:
        usage = response_data.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        
        if total_tokens > 0:
            # Simple cost heuristic for MVP: $0.002 per 1K tokens
            cost_dollars = (total_tokens / 1000.0) * 0.002
            
            async with httpx.AsyncClient() as client:
                await client.post(f"{CONTROL_PLANE_URL}/policies/{tenant_id}/usage", json={
                    "tokens": total_tokens,
                    "cost": cost_dollars
                }, timeout=2.0)
    except Exception as e:
        print(f"Failed to report usage: {e}")

def track_billing(tenant_id: str, response_data: dict):
    """
    Fires off the asynchronous usage reporter.
    """
    asyncio.create_task(report_usage_async(tenant_id, response_data))
