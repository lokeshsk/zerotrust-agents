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
