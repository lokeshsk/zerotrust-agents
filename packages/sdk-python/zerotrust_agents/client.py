import httpx
from .resources.policies import Policies
from .resources.logs import Logs
from .resources.approvals import Approvals

class ZeroTrustAgents:
    """
    Client for interacting with the ZeroTrust Agents Control Plane API.
    Follows the nested resource pattern.
    """
    def __init__(self, api_key: str, tenant_id: str = "default", base_url: str = "http://localhost:8001"):
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.base_url = base_url
        
        self._http_client = httpx.Client(base_url=self.base_url)

        # Resources
        self.policies = Policies(self)
        self.logs = Logs(self)
        self.approvals = Approvals(self)

    def close(self):
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
