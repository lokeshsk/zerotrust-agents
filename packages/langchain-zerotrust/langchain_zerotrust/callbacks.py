import logging
import json
import time
from typing import Any, Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

class ZeroTrustCallbackHandler(BaseCallbackHandler):
    """
    LangChain Callback Handler that integrates with ZeroTrust Agents.
    Intercepts tool calls before they are executed and checks the firewall policy.
    """
    def __init__(self, agent_id: str, api_key: str, base_url: str = "http://localhost:8001", tenant_id: str = "default"):
        super().__init__()
        self.agent_id = agent_id
        
        try:
            from zerotrust_agents import ZTAClient
            self.client = ZTAClient(api_key=api_key, tenant_id=tenant_id, base_url=base_url)
        except ImportError:
            raise ImportError("Please install zerotrust-agents-sdk: pip install zerotrust-agents-sdk")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Run when a tool starts running."""
        tool_name = serialized.get("name", "unknown_tool")
        
        # input_str is usually a JSON string for structured tools, or plain string
        arguments = {}
        try:
            arguments = json.loads(input_str)
        except:
            arguments = {"input": input_str}
            
        try:
            action = self.client.policies.check(
                agent_id=self.agent_id,
                tool_name=tool_name,
                arguments=arguments
            )
            
            if action == "allow":
                return
            elif action == "require_approval":
                # Create a pending approval via the SDK
                # For LangChain sync execution, we block and wait for approval
                approval = self.client.approvals.create(
                    agent_id=self.agent_id,
                    tool_name=tool_name,
                    arguments=json.dumps(arguments)
                )
                approval_id = approval.get("id")
                
                logger.info(f"[{self.agent_id}] Tool {tool_name} requires approval. Suspending... (ID: {approval_id})")
                
                # Poll for approval
                is_allowed = False
                for _ in range(30): # Wait up to 60 seconds
                    status_info = self.client.approvals.get(approval_id)
                    status = status_info.get("status")
                    if status == "approved":
                        is_allowed = True
                        break
                    elif status == "rejected":
                        is_allowed = False
                        break
                    time.sleep(2)
                    
                if not is_allowed:
                    # Log the blocked call
                    self.client.logs.create(
                        agent_id=self.agent_id,
                        tool_name=tool_name,
                        arguments=json.dumps(arguments),
                        allowed=False
                    )
                    raise RuntimeError(f"ZeroTrust Agents Blocked: Administrator rejected execution of '{tool_name}'.")
                    
                # Log the allowed call
                self.client.logs.create(
                    agent_id=self.agent_id,
                    tool_name=tool_name,
                    arguments=json.dumps(arguments),
                    allowed=True
                )
            else:
                # Log the blocked call
                self.client.logs.create(
                    agent_id=self.agent_id,
                    tool_name=tool_name,
                    arguments=json.dumps(arguments),
                    allowed=False
                )
                raise RuntimeError(f"ZeroTrust Agents Blocked: You are not authorized to use the tool '{tool_name}'.")
                
        except Exception as e:
            if isinstance(e, RuntimeError) and "ZeroTrust Agents Blocked" in str(e):
                raise e
            logger.error(f"ZeroTrust Callback Error: {e}")
            # Fail closed on API errors
            raise RuntimeError(f"ZeroTrust Agents Security Error: Could not verify tool permissions for '{tool_name}'.")
