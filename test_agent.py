import httpx
import os

# 1. Setup our testing environment
CONTROL_PLANE_URL = "http://localhost:8001"
GATEWAY_URL = "http://localhost:8006/v1"
AGENT_ID = "sales-assistant"

# The real OpenAI key would be needed if testing actual LLM generation,
# but our LiteLLM gateway can forward whatever we send. 
# We'll mock the tool call logic for the test to ensure the proxy blocks it.

def setup_policy():
    print("--- 1. Setting up Policies in Control Plane ---")
    # Allow web search
    httpx.post(f"{CONTROL_PLANE_URL}/policies/", json={
        "agent_id": AGENT_ID,
        "tool_name": "search_web",
        "action": "allow"
    })
    # Deny database deletion
    httpx.post(f"{CONTROL_PLANE_URL}/policies/", json={
        "agent_id": AGENT_ID,
        "tool_name": "delete_db",
        "action": "deny"
    })
    # Require approval for SQL execution
    httpx.post(f"{CONTROL_PLANE_URL}/policies/", json={
        "agent_id": AGENT_ID,
        "tool_name": "execute_sql",
        "action": "require_approval"
    })
    print("✅ Policies seeded into Postgres database.\n")

def test_agent_tool_call(tool_name: str):
    print(f"--- 2. Agent Attempting to use tool: {tool_name} ---")
    print(f"Agent '{AGENT_ID}' is sending request to Gateway {GATEWAY_URL}...")
    
    headers = {
        "x-agent-id": AGENT_ID,
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', 'sk-fake')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Use the {tool_name} tool."}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": f"Test {tool_name}"
                }
            }
        ],
        "tool_choice": {"type": "function", "function": {"name": tool_name}}
    }
    
    try:
        response = httpx.post(f"{GATEWAY_URL}/chat/completions", headers=headers, json=payload, timeout=30.0)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {})
            if "SYSTEM FIREWALL BLOCK" in (message.get("content") or ""):
                print(f"🛡️ FIREWALL SUCCESSFULLY BLOCKED: {tool_name}")
            else:
                print(f"🔓 FIREWALL ALLOWED: {tool_name} -> {result}")
        elif response.status_code == 502:
            print(f"⚠️ Gateway returned 502 Bad Gateway.")
            print(f"Detail: {response.json().get('detail')}")
            print("Note: The firewall auto-discovered your tools, but requires an OPENAI_API_KEY in .env to actually forward the LLM request to OpenAI!\n")
        else:
            print(f"❌ Gateway returned error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error testing gateway: {e}\n(Make sure the Gateway and Control Plane are running!)")

def test_semantic_dlp():
    print(f"\n--- 3. Testing Semantic DLP (Data Loss Prevention) ---")
    print(f"Agent '{AGENT_ID}' is attempting to run a destructive SQL query...")
    
    # We pass a payload that contains "DROP TABLE" to trigger the DLP Regex
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Execute destructive query."}],
        "tools": [{"type": "function", "function": {"name": "execute_sql", "description": "dummy"}}],
        "tool_choice": {"type": "function", "function": {"name": "execute_sql", "arguments": "{\"query\": \"DROP TABLE users;\"}"}}
    }
    
    try:
        response = httpx.post(f"{GATEWAY_URL}/chat/completions", headers={"x-agent-id": AGENT_ID}, json=payload, timeout=5.0)
        if response.status_code == 200:
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {})
            if "Semantic DLP Block" in (message.get("content") or ""):
                print(f"🛡️ FIREWALL SUCCESSFULLY BLOCKED via DLP: {message.get('content')}")
            else:
                print(f"❌ DLP FAILED. Request went through: {result}")
    except Exception as e:
        print(f"Error testing gateway: {e}")

def test_rate_limiting():
    print(f"\n--- 4. Testing Anomaly Detection (Rate Limiting) ---")
    print(f"Agent '{AGENT_ID}' is attempting to flood the API (4 requests in <10s)...")
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Spam request"}],
    }
    
    blocked = False
    for i in range(4):
        try:
            response = httpx.post(f"{GATEWAY_URL}/chat/completions", headers={"x-agent-id": AGENT_ID}, json=payload, timeout=2.0)
            if response.status_code == 429:
                print(f"🛡️ FIREWALL SUCCESSFULLY BLOCKED via Rate Limiting: {response.json().get('error')}")
                blocked = True
                break
            else:
                print(f"   Request {i+1} allowed...")
        except Exception as e:
            pass
            
    if not blocked:
        print("❌ Rate Limiting FAILED. All requests allowed.")

if __name__ == "__main__":
    setup_policy()
    test_agent_tool_call("search_web")
    print("\n")
    test_agent_tool_call("delete_db")
    print("\n")
    
    # New Billion-Dollar Features!
    test_semantic_dlp()
    test_rate_limiting()
    
    # We leave the HITL test for last because it freezes the terminal
    print("\n--- 5. Testing Human-in-the-Loop (Requires Dashboard Approval) ---")
    test_agent_tool_call("execute_sql")

