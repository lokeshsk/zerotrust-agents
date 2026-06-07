# ZeroTrust Agents Python SDK

The official Python SDK for interacting with the [ZeroTrust Agents](https://github.com/lokeshsk/zerotrust-agents) Control Plane.

## Installation

```bash
pip install zerotrust-agents-sdk
```

## Usage

```python
from zerotrust_agents import ZeroTrustAgents

client = ZeroTrustAgents(api_key="your-master-key")

# Check if an agent is allowed to execute a tool
action = client.policies.check(
    agent_id="my-agent-123",
    tool_name="execute_sql",
    arguments={"query": "SELECT * FROM users"}
)
print(action) # 'allow', 'deny', or 'require_approval'

# Wait for a human to approve an action
if action == "require_approval":
    approval_id = client.approvals.create(
        agent_id="my-agent-123",
        tool_name="execute_sql",
        arguments='{"query": "SELECT * FROM users"}'
    )
    is_allowed = client.approvals.wait(approval_id)
    print("Was approved?", is_allowed)

# Log a tool execution
client.logs.create(
    agent_id="my-agent-123",
    tool_name="execute_sql",
    arguments='{"query": "SELECT * FROM users"}',
    allowed=True
)
```
