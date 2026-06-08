<p align="center">
  <img src="logo.png" alt="Agent Firewall Logo" width="120" />
</p>

<h1 align="center">Zero Trust Agents</h1>

<p align="center">
  <strong>The definitive security and observability control plane for Autonomous AI Agents.</strong>
</p>

<p align="center">
  <a href="https://github.com/lokeshsk/zerotrust-agents/stargazers"><img src="https://img.shields.io/github/stars/lokeshsk/zerotrust-agents?style=for-the-badge&color=yellow" alt="Stars" /></a>
  <a href="https://github.com/lokeshsk/zerotrust-agents/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lokeshsk/zerotrust-agents?style=for-the-badge&color=blue" alt="License" /></a>
  <a href="https://zerotrust-agents.com"><img src="https://img.shields.io/website?url=https%3A%2F%2Fzerotrust-agents.com&style=for-the-badge&label=Website" alt="Website" /></a>
  <a href="https://docs.zerotrust-agents.com"><img src="https://img.shields.io/badge/Docs-Live-green?style=for-the-badge" alt="Docs" /></a>
</p>

<!-- 
TODO: Add Demo GIF or YouTube Video embed here
Example: 
<p align="center">
  <a href="https://youtu.be/YOUR_VIDEO_ID"><img src="https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg" alt="Agent Firewall Demo" width="800"></a>
</p>
-->

<p align="center">
  <a href="#quickstart">Quickstart</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#mcp-model-context-protocol">MCP Protocol</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#enterprise-edition">Enterprise Edition</a>
</p>

---

## Why ZeroTrust Agents (ZTA)?
As AI Agents become increasingly autonomous (executing SQL, calling external APIs, writing to databases), organizations need a centralized security layer to prevent rogue actions, ensure compliance, and monitor AI behavior in real time.

**ZeroTrust Agents (ZTA)** acts as an enterprise-grade API Gateway that sits securely between your AI Agent and its LLM provider (OpenAI, Anthropic, Gemini, etc.). It intercepts the agent's attempts to use tools and evaluates those actions against a strict, zero-trust security policy engine before allowing them to execute.

## Features
- **LiteLLM Proxy Engine**: Agnostic proxy that intercepts traffic and forces LLMs to adhere to predefined tool-use policies. We support the `OpenAI`, `Anthropic`, and `Gemini` tool-use specification formats natively.
- **Semantic DLP**: Scans arguments sent to tools for destructive commands (e.g., `DROP TABLE`) and PII using secondary lightweight local LLMs. Go beyond regex.
- **Human-in-the-Loop (HITL)**: Suspend high-risk agent operations until a human administrator clicks "Approve" or "Block" in the visual dashboard.
- **Auto-Discovery Graph**: Automatically maps and visualizes the relationships between your AI agents and the external tools they are trying to use.
- **🔌 Model Context Protocol (MCP)**: Native support for Anthropic's MCP, allowing you to proxy MCP tool calls natively through the gateway.
- **🐍 Python SDK & CLI (`zta`)**: Official SDK (`zerotrust-agents-sdk`) to interact programmatically with the Firewall control plane, complete with a powerful CLI tool to sync policies, apply predefined security templates (e.g. `safe_github`), and manage approvals.
- **🔔 Real-time Alerting**: Instantly fire webhooks to Slack or Discord whenever an agent attempts a high-risk action requiring Human-in-the-Loop approval.
- **👥 Multi-Tenancy Setup**: The entire architecture is partitioned by `tenant_id`. Built from the ground-up to support SaaS deployments or internal enterprise isolation.
- **🔒 Completely Offline**: Can be run entirely offline or air-gapped without relying on any external cloud backends.

## 🚀 Authentication & API Keys

ZeroTrust Agents is completely self-hosted, meaning you control the keys!

- **The Master Key**: In your `.env` file, there is a `SECRET_KEY`. This is your admin key used to authenticate the `zta` CLI and Python SDK with your local Control Plane.
- **Agent API Keys**: The system automatically seeds a "Default Organization" with the API key `sk-default`. Your agents use this in their `Authorization: Bearer sk-default` headers when talking to the Gateway.

## Quickstart

Getting started is easy. You can run the entire Agent Firewall stack (Gateway, API, Database, and Dashboard) locally with a single command.

### 1. 1-Click Launch
We provide an interactive launcher that manages dependencies for you.

```bash
git clone https://github.com/lokeshsk/zerotrust-agents.git
cd zerotrust-agents
chmod +x start.sh

# Run the interactive setup!
./start.sh
```

### 2. Install the CLI & SDK
Manage your firewall directly from the terminal.

```bash
pip install zerotrust-agents-sdk

# Login using the SECRET_KEY from your .env
zta login my-super-secret-key --url http://localhost:8001
```

### 3. Apply a Security Template
```bash
# Instantly secure an agent by blocking destructive SQL queries
zta templates apply read_only_sql --agent-id data-analyst-agent
```

### 4. Route your Agent Traffic
In your AI application (e.g. using LiteLLM, LangChain, or OpenAI SDK), point the base URL to the Gateway and pass the default tenant API key:

```python
from openai import OpenAI

# The firewall acts as a proxy, so you use your Gateway's URL
client = OpenAI(
    api_key="sk-default", # The default Tenant API Key
    base_url="http://localhost:8000/v1"
)
```

Once booted, open the Dashboard at: **[http://localhost:3000](http://localhost:3000)** (or your custom `APP_URL`).

### Environment Variables
Upon first launch, `./start.sh` automatically copies `.env.example` to `.env`. 
Open `.env` and set your Upstream API Keys so the Gateway can route requests for your agents:
```env
OPENAI_API_KEY="sk-your-openai-key"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
APP_URL="http://localhost:3000"
```

## Architecture

```mermaid
graph TD
    A[Autonomous AI Agent] -->|Tool Call Request| G[Agent Firewall Gateway]
    
    subgraph Control Plane
    G <-->|Policy Check| API[FastAPI Server]
    API <--> DB[(PostgreSQL)]
    end

    subgraph External
    G -->|If Allowed| LLM[OpenAI / Anthropic]
    end
    
    D[Admin Dashboard] --> API
```

1. **Gateway (`apps/gateway/`)**: A high-performance proxy written in Python/FastAPI. Intercepts agent traffic, runs anomaly detection, extracts requested tool invocations, evaluates policies, and queries the Control Plane.
2. **API Control Plane (`apps/api/`)**: A backend managing Workspaces, Policies, Audit Logs, and pending HITL approvals.
3. **Dashboard (`apps/web/`)**: A Next.js 15 frontend App Console utilizing Tailwind CSS and a premium dark-mode aesthetic.
4. **Website & Docs (`apps/website/` and `apps/docs/`)**: Next.js applications that serve the main landing page and Fumadocs-powered documentation, tied together using Next.js Multi-Zones.

## MCP (Model Context Protocol)

**ZTA** natively supports Anthropic's **Model Context Protocol (MCP)**.
Instead of giving LLMs unmitigated direct access to your local filesystem or databases, you can route your MCP connections through the Firewall.
The Gateway intercepts the JSON-RPC messages, inspects the `CallToolRequest`, and blocks actions like `write_file` or `execute_query` based on your policies, all while keeping the connection stateful.

## Documentation

Comprehensive documentation is available for deployment, configuration, and writing custom Semantic DLP plugins.
To run the documentation locally:
```bash
turbo run dev --filter=docs
```

## Open Source vs Enterprise Edition
Agent Firewall operates on an Open Core model. 

* **Community Edition (Open Source)**: Includes the core firewall proxy, semantic DLP, basic HITL flows, and master key authentication.
* **Enterprise Edition (EE)**: Distributed privately for enterprise customers. Unlocks:
  - Auth0 / Active Directory SSO
  - Multi-Tenant Workspaces & RBAC
  - Advanced SIEM Webhooks (Splunk/Datadog)
  - Cost Controls & Hard Billing Budgets

*If you are interested in an Enterprise License, please visit our website at [zerotrust-agents.com](https://zerotrust-agents.com).*

---
<p align="center">
  Built with ❤️ for secure AI.
</p>
