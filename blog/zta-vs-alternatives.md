---
title: "Why Framework-Level Security Fails for AI Agents (And How to Fix It)"
published: false
description: "Why bolting security onto LangChain or CrewAI is a bad idea, and how API Gateways solve the Agentic security problem."
tags: "python, opensource, artificialintelligence, security"
cover_image: "https://zerotrust-agents.com/og-image.jpg"
---

When an engineering team builds an autonomous AI agent, they usually start by hardcoding security directly into the agent's framework. 

If they are using **LangChain**, they might write a custom `@tool` decorator that checks a user's permissions before running. If they are using **CrewAI**, they might write a Python `if/else` statement inside the agent's execution loop. 

This is known as **Framework-Level Security**, and for enterprise deployments, it is a disaster waiting to happen.

To solve this, I built **[ZeroTrust Agents](https://github.com/lokeshsk/zerotrust-agents)**, an open-source deterministic API gateway for your AI agents. 

Securing your agent with it is as simple as changing one line of code:

```python
import openai

# To secure your agent, you just change the base_url
client = openai.OpenAI(
    base_url="http://localhost:8000/v1", # 🛡️ Route through ZeroTrust Agents
    api_key="your-openai-key"
)
```

Here is why you should be moving security out of your agent code and into the network layer.

---

## ❌ The Problem with Framework-Level Security

If you rely on your Python framework or the LLM's prompt to enforce security, you run into three critical bottlenecks:

### 1. It's Not Polyglot
In a mid-sized enterprise, one team might use LangChain in Python, another might use AutoGen in TypeScript, and a third might write raw HTTP calls in Go. If security is tied to the framework, every team has to re-implement the security checks (and keep them updated) from scratch in their respective languages.

### 2. It Relies on LLM Compliance
Many framework-level checks happen *after* the tool payload is parsed but *before* the function executes. However, an adversarial prompt injection can often trick the framework's parser or cause the LLM to output malformed JSON that crashes the validation logic entirely. 

### 3. No Centralized Audit Trail
If every agent implements its own security natively, the CISO has no single pane of glass to view what these agents are doing across the organization. Auditing becomes a fragmented nightmare.

---

## ✅ The Gateway Paradigm (ZeroTrust Agents)

**ZeroTrust Agents** moves security out of the application code and into the network layer. 

By functioning as a transparent reverse proxy between your agents and the upstream LLM (OpenAI, Anthropic, Gemini) or Model Context Protocol (MCP) server, it provides **Network-Level Security**.

Why is this architectural shift so much better?

* 🌍 **Universal Compatibility:** It doesn't matter if you wrote your agent in Python, Rust, or Bash. If your agent makes an API call to an LLM to request a tool, the Gateway intercepts the stream. 
* 📝 **Centralized Policy-as-Code:** Security teams can define YAML rules that apply globally. For example: *"No agent in the production environment may call `execute_sql` without human approval."*
* 🛑 **Human-in-the-Loop:** Because the proxy holds the HTTP connection open, it can suspend the agent's execution entirely, send a Slack message to an admin, and wait for them to click "Approve" before allowing the tool to run.
* 👁️ **Single Pane of Glass:** Every tool call attempt—whether allowed or blocked—is logged centrally in the ZeroTrust dashboard. 

### Security should never be an afterthought

Security cannot be a bolt-on patch to an agent framework. It must be a foundational, decoupled layer. 

If you are building AI agents that touch production data, check out **[ZeroTrust Agents on GitHub](https://github.com/lokeshsk/zerotrust-agents)**. We are completely open-source and would love for you to spin up the Docker container, try it out, and leave us a ⭐ if you find it useful!

**How are you currently securing your AI agents? Let me know in the comments below! 👇**
