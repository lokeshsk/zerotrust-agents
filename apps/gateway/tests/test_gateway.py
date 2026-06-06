import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)

def test_gateway_health():
    response = client.get("/")
    assert response.status_code == 200

def test_openai_proxy_no_auth():
    response = client.post("/v1/chat/completions", json={"model": "gpt-4", "messages": []})
    assert response.status_code == 401

def test_anthropic_proxy_no_auth():
    response = client.post("/v1/messages", json={"model": "claude-3", "messages": []})
    assert response.status_code == 401

def test_gemini_proxy_no_auth():
    response = client.post("/v1/models/gemini-1.5-pro:generateContent", json={"contents": []})
    assert response.status_code == 401
