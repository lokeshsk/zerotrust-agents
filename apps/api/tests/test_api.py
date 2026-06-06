import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_resolve_key_unauthorized():
    response = client.get("/tenants/resolve-key?api_key=invalid")
    assert response.status_code == 401

def test_policies_unauthorized():
    response = client.get("/policies/tenant-123/agent-123/tool-123")
    assert response.status_code == 401 # Missing gateway secret
