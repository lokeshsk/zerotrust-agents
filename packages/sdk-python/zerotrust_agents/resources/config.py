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
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json()
