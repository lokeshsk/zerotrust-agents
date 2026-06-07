# How ZeroTrust Agents Works Under the Hood

When we set out to build a security layer for AI agents, we realized we couldn't ask developers to rewrite their entire stack. The ecosystem is moving too fast. If a team is using OpenAI's SDK today, they might switch to Anthropic tomorrow, and Gemini the next day. 

We needed a solution that was entirely agnostic to the framework, the LLM, and the language. 

That's why **ZeroTrust Agents** is built as a transparent API Gateway.

## The Proxy Architecture

At its core, ZeroTrust Agents is a high-performance Python FastAPI reverse proxy. To use it, developers change exactly one line of code in their application: the `base_url` of their LLM SDK.

When your agent tries to generate a completion using `client.chat.completions.create(...)`, the request flows into the ZeroTrust Gateway. The Gateway forwards the prompt to OpenAI or Anthropic, but it actively intercepts the *response stream*. 

If the LLM decides to call a tool (e.g., passing a JSON payload to `execute_sql`), the Gateway pauses the stream. It buffers the JSON chunks until the full tool payload is constructed. 

## The Policy Engine

Once the payload is buffered, the Gateway queries its distributed Redis Policy Engine to answer three questions:

1. **Identity & RBAC:** Is `Agent-Alpha` allowed to use the tool `execute_sql` in this workspace?
2. **Semantic DLP:** Does the payload `{"query": "DROP TABLE users;"}` contain malicious intent or sensitive PII?
3. **Approval:** Does this tool require Human-in-the-Loop (HITL) approval?

If the DLP engine flags the payload, or the policy denies access, the Gateway modifies the LLM's response mid-stream. It injects a system-level block message into the stream, effectively telling the agent: `"SYSTEM FIREWALL BLOCK: You are not authorized."` The tool is never executed on your infrastructure.

## Human-in-the-Loop (HITL)

The most powerful feature of this architecture is the ability to suspend execution. If a policy requires approval, the Gateway emits a WebSocket event to the Admin Dashboard (or a Slack webhook) and suspends the HTTP stream using `asyncio` primitives. 

The agent client remains hanging on the HTTP request. Once a human administrator reviews the payload and clicks "Approve", the Gateway releases the suspension, yields the tool call chunk to the client, and the agent completes its workflow as if nothing happened.

By operating at the network layer, ZeroTrust Agents provides deterministic security without requiring you to change how your agents are built.
