import os
import yaml

class Templates:
    def __init__(self, client):
        self._client = client
        self._templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    def list(self) -> list[str]:
        """List available built-in policy templates."""
        if not os.path.exists(self._templates_dir):
            return []
        return [f.replace(".yaml", "") for f in os.listdir(self._templates_dir) if f.endswith(".yaml")]

    def apply(self, template_name: str, agent_id: str) -> dict:
        """Apply a built-in template to a specific agent."""
        if not template_name.endswith(".yaml"):
            template_name += ".yaml"
        
        file_path = os.path.join(self._templates_dir, template_name)
        if not os.path.exists(file_path):
            raise ValueError(f"Template '{template_name}' not found.")
            
        with open(file_path, "r") as f:
            template_content = f.read()
            
        # Replace template placeholders if any, or just parse
        # If the template requires dynamic agent_id injection, we can parse it
        parsed = yaml.safe_load(template_content)
        
        # Inject the target agent_id into all rules
        if "policies" in parsed:
            for p in parsed["policies"]:
                p["agent_id"] = agent_id
        
        # We can use the policies.sync logic on the server, but it expects a file. 
        # For simplicity, we can loop and create them, or use a new bulk sync endpoint.
        # The /policies/sync-yaml endpoint exists and expects a multipart form file.
        import io
        import httpx
        
        # Dump the modified yaml back to string
        modified_yaml = yaml.dump(parsed)
        files = {"file": ("template.yaml", io.BytesIO(modified_yaml.encode("utf-8")), "application/x-yaml")}
        
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
