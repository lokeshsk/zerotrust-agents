import httpx
import time

class Approvals:
    def __init__(self, client):
        self._client = client

    def create(self, agent_id: str, tool_name: str, arguments: str) -> int:
        """Create a pending Human-in-the-Loop approval request."""
        resp = self._client._http_client.post(
            "/policies/approvals",
            json={
                "tenant_id": self._client.tenant_id,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "arguments": arguments
            },
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json().get("id")

    def wait(self, approval_id: int, timeout: int = 60) -> bool:
        """Poll the control plane until the approval is either 'approved' or 'rejected'."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = self._client._http_client.get(
                    f"/policies/approvals/{approval_id}",
                    headers={"x-gateway-secret": self._client.api_key}
                )
                if resp.status_code == 200:
                    status = resp.json().get("status")
                    if status == "approved":
                        return True
                    elif status == "rejected":
                        return False
            except Exception:
                pass
            time.sleep(2)
        return False
