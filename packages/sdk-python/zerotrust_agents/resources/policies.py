import os
import httpx

class Policies:
    def __init__(self, client):
        self._client = client

    def check(self, agent_id: str, tool_name: str, arguments: dict) -> str:
        """
        Check if an agent is allowed to execute a specific tool with the given arguments.
        Returns: 'allow', 'deny', or 'require_approval'
        """
        import json
        resp = self._client._http_client.get(
            f"/policies/{self._client.tenant_id}/{agent_id}/{tool_name}",
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        data = resp.json()
        action = data.get("action", "deny")
        dsl_rules_str = data.get("dsl_rules")

        if dsl_rules_str and action == "allow":
            # Simple wrapper since actual DSL evaluation happens on Gateway usually
            pass

        return action

    def register(self, agent_id: str, tools: list[str]):
        """Auto-register tools for an agent"""
        resp = self._client._http_client.post(
            "/policies/register",
            json={"tenant_id": self._client.tenant_id, "agent_id": agent_id, "tools": tools},
            headers={"x-gateway-secret": self._client.api_key}
        )
        resp.raise_for_status()
        return resp.json()

    def sync(self, file_path: str) -> dict:
        """Sync a local YAML policy file to the control plane."""
        import io
        with open(file_path, "rb") as f:
            content = f.read()
            
        files = {"file": (os.path.basename(file_path), io.BytesIO(content), "application/x-yaml")}
        resp = self._client._http_client.post(
            "/policies/sync-yaml",
            files=files,
            headers={
                "x-gateway-secret": self._client.api_key,
                "x-tenant-id": self._client.tenant_id
            }
        )
        resp.raise_for_status()
        return resp.json()
