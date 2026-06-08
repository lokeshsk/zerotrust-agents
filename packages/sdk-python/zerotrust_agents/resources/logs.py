import httpx

class Logs:
    def __init__(self, client):
        self._client = client

    def create(self, agent_id: str, tool_name: str, arguments: str, allowed: bool):
        """Log a tool execution event to the control plane."""
        resp = self._client._http_client.post(
            "/logs/",
            json={
                "tenant_id": self._client.tenant_id,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "arguments": arguments,
                "allowed": allowed
            },
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json()

    def list(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Fetch recent audit logs."""
        resp = self._client._http_client.get(
            f"/logs/?skip={skip}&limit={limit}",
            headers={
                "x-gateway-secret": self._client.api_key,
                "x-tenant-id": self._client.tenant_id
            }
        )
        resp.raise_for_status()
        return resp.json()
