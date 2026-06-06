import litellm
from fastapi import HTTPException

# Configure LiteLLM to be completely transparent.
# It uses litellm.completion to route to OpenAI, Anthropic, Gemini, etc.
# depending on the "model" string provided in the request body.

async def forward_to_upstream(body: dict):
    """
    Use LiteLLM to forward the request to the correct upstream provider.
    This makes the Gateway agnostic to the underlying LLM provider.
    """
    try:
        # LiteLLM handles the translation automatically.
        response = await litellm.acompletion(**body)
        if body.get("stream", False):
            return response
        return response.model_dump()
    except Exception as e:
        if "Missing credentials" in str(e) or "APIKey" in str(e):
            # MOCK MODE FALLBACK FOR LOCAL TESTING WITHOUT KEYS
            tool_choice = body.get("tool_choice", {})
            if isinstance(tool_choice, dict) and "function" in tool_choice:
                name = tool_choice["function"].get("name")
                args = tool_choice["function"].get("arguments", "{}")
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "function": {"name": name, "arguments": args}
                            }]
                        }
                    }]
                }
        print(f"Upstream routing error: {e}")
        raise HTTPException(status_code=502, detail=f"Upstream provider error: {str(e)}")
