class Config:
    def __init__(self, client):
        self._client = client

    def get(self) -> dict:
        """Get the current configuration for the tenant."""
        resp = self._client._http_client.get(
            f"/policies/{self._client.tenant_id}/config",
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json()

    def set(self, **kwargs) -> dict:
        """
        Update the tenant configuration.
        Example: client.config.set(hitl_webhook_url="https://hooks.slack.com/...")
        """
        # Exclude None values
        payload = {k: v for k, v in kwargs.items() if v is not None}
        resp = self._client._http_client.post(
            f"/policies/{self._client.tenant_id}/config",
            json=payload,
            headers={"Authorization": f"Bearer {self._client.api_key}"}
        )
        resp.raise_for_status()
        return resp.json()

    def get_agent(self, agent_id: str) -> dict:
        """Get the current budget and spend for an agent."""
        resp = self._client._http_client.get(
            f"/policies/{self._client.tenant_id}/agents/{agent_id}",
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json()

    def set_agent_budget(self, agent_id: str, budget_limit: int) -> dict:
        """Set the hard budget limit (in cents) for a specific agent."""
        resp = self._client._http_client.post(
            f"/policies/{self._client.tenant_id}/agents/{agent_id}/budget",
            json={"budget_limit": budget_limit},
            headers={"Authorization": f"Bearer {self._client.api_key}"}
        )
        resp.raise_for_status()
        return resp.json()
