import requests
import json
from typing import Optional, Dict, Any, List

class AgentFirewall:
    def __init__(self, api_key: str, control_plane_url: str = "http://localhost:8001"):
        """
        Initialize the ZeroTrust Agents Firewall SDK.
        
        :param api_key: The workspace master key or agent API key
        :param control_plane_url: The URL of the Control Plane API
        """
        self.api_key = api_key
        self.base_url = control_plane_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def get_policies(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        """List all active policies for a workspace."""
        resp = self.session.get(f"{self.base_url}/policies/", headers={"x-tenant-id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def create_policy(self, agent_id: str, tool_name: str, action: str, dsl_rules: Optional[Dict] = None, tenant_id: str = "default") -> Dict[str, Any]:
        """Create or update a policy."""
        payload = {
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "action": action
        }
        if dsl_rules:
            payload["dsl_rules"] = json.dumps(dsl_rules)
            
        resp = self.session.post(f"{self.base_url}/policies/", json=payload, headers={"x-tenant-id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def get_logs(self, limit: int = 100, tenant_id: str = "default") -> List[Dict[str, Any]]:
        """Fetch audit logs."""
        resp = self.session.get(f"{self.base_url}/logs/?limit={limit}", headers={"x-tenant-id": tenant_id})
        resp.raise_for_status()
        return resp.json()
