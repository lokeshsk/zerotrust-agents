<p align="center">
  <img src="https://raw.githubusercontent.com/agent-firewall/assets/main/logo.png" alt="Agent Firewall Logo" width="120" />
</p>

<h1 align="center">Agent Firewall 🛡️</h1>

<p align="center">
  <strong>The definitive security and observability control plane for Autonomous AI Agents.</strong>
</p>

<p align="center">
  <a href="#quickstart">Quickstart</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#enterprise-edition">Enterprise Edition</a>
</p>

---

## What We Are Building
As AI Agents become increasingly autonomous (executing SQL, calling external APIs, writing to databases), organizations need a centralized security layer to prevent rogue actions, ensure compliance, and monitor AI behavior in real time.

**Agent Firewall** is an enterprise-grade API Gateway that sits securely between your AI Agent and its LLM provider (OpenAI, Anthropic, Gemini, etc.). It intercepts the agent's attempts to use tools and evaluates those actions against a strict, zero-trust security policy engine before allowing them to execute.

## Features
- **🔥 LiteLLM Proxy Engine**: Agnostic proxy that intercepts traffic and forces LLMs to adhere to predefined tool-use policies.
- **🛡️ Semantic DLP**: Scans arguments sent to tools for destructive commands (e.g., `DROP TABLE`) and PII using secondary lightweight local LLMs.
- **⏸️ Human-in-the-Loop (HITL)**: Suspend high-risk agent operations until a human administrator clicks "Approve" or "Block" in the visual dashboard.
- **🗺️ Auto-Discovery Graph**: Automatically maps and visualizes the relationships between your AI agents and the external tools they are trying to use.
- **👥 Multi-Tenancy Setup**: The entire architecture is partitioned by `tenant_id` for SaaS deployments.

## Quickstart

Getting started is easy. You can run the entire Agent Firewall stack (Gateway, API, Database, and Dashboard) locally with a single command.

### 1-Click Launch
We provide an interactive launcher that manages dependencies for you.

```bash
git clone https://github.com/your-org/agent-firewall.git
cd agent-firewall
chmod +x start.sh

# Run the interactive setup!
./start.sh
```

When prompted, select **[1] Docker Compose (Recommended)** to spin up the containerized stack, or **[2] Natively** to run it directly on your machine (Requires Python 3.10+, Node 20+, and PostgreSQL).

Once booted, open the Dashboard at: **[http://localhost:3000](http://localhost:3000)**

### Environment Variables
Upon first launch, `./start.sh` automatically copies `.env.example` to `.env`. 
Open `.env` and set your Upstream API Keys so the Gateway can route requests for your agents:
```env
OPENAI_API_KEY="sk-your-openai-key"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
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

1. **Gateway (`apps/gateway/`)**: A high-performance proxy. Intercepts agent traffic, runs anomaly detection, extracts requested tool invocations, and queries the Control Plane.
2. **API Control Plane (`apps/api/`)**: A backend managing Workspaces, Policies, Audit Logs, and pending HITL approvals.
3. **Dashboard (`apps/web/`)**: A Next.js 14 frontend utilizing Tailwind CSS and a premium dark-mode aesthetic.

## Open Source vs Enterprise Edition
Agent Firewall operates on an Open Core model. 

* **Community Edition (Open Source)**: Includes the core firewall proxy, semantic DLP, basic HITL flows, and master key authentication.
* **Enterprise Edition (EE)**: Distributed privately for enterprise customers. Unlocks:
  - Auth0 / Active Directory SSO
  - Multi-Tenant Workspaces & RBAC
  - Advanced SIEM Webhooks (Splunk/Datadog)
  - Cost Controls & Hard Billing Budgets

*If you are interested in an Enterprise License, please visit our website.*

---
<p align="center">
  Built with ❤️ for secure AI.
</p>
