# LangChain ZeroTrust Agents Middleware

This package provides a LangChain Callback Handler that integrates directly with the **ZeroTrust Agents** control plane.

Instead of routing your agent's LLM traffic through the ZeroTrust Gateway proxy, you can use this callback handler to natively enforce security policies during LangChain tool execution.

## Installation

```bash
pip install langchain-zerotrust zerotrust-agents-sdk
```

## Usage

Simply attach the `ZeroTrustCallbackHandler` to your LangChain agent or tools.

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool
from langchain_zerotrust import ZeroTrustCallbackHandler

# 1. Initialize the ZeroTrust Callback
zta_callback = ZeroTrustCallbackHandler(
    agent_id="langchain-bot-1",
    api_key="sk-your-tenant-api-key",
    base_url="http://localhost:8001" # Point to your ZeroTrust Control Plane
)

# 2. Define your tools
def execute_sql(query: str):
    return "Executed: " + query

sql_tool = Tool(
    name="execute_sql",
    func=execute_sql,
    description="Executes a SQL query on the database."
)

# 3. Create the agent with the callback
llm = OpenAI(temperature=0)
agent = initialize_agent(
    [sql_tool], 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    callbacks=[zta_callback] # <--- Attach here!
)

# 4. Run the agent
# If the policy for 'execute_sql' is set to 'deny', the callback will raise a RuntimeError
# If it is set to 'require_approval', the callback will suspend execution and wait for admin approval via the Dashboard or Slack.
try:
    agent.run("Drop the users table using execute_sql")
except RuntimeError as e:
    print(f"Agent stopped by firewall: {e}")
```

## Features Supported
- **Policy Enforcement**: Blocks tools natively based on your ZeroTrust rules.
- **Human-in-the-Loop (HITL)**: Automatically suspends the agent's Python thread and polls for approval.
- **Audit Logging**: Logs every tool execution (allowed or blocked) directly to the ZeroTrust Dashboard.
