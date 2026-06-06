import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # To import ee

from fastapi import FastAPI, Response
from routers import openai_proxy
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

try:
    from ee.license import is_ee_active
    EE_ACTIVE = is_ee_active()
except ImportError:
    EE_ACTIVE = False

print(f"--- Enterprise Edition Active: {EE_ACTIVE} ---")

app = FastAPI(title="Agent Firewall Gateway Proxy")

# Include modular routers
app.include_router(openai_proxy.router)

@app.get("/")
def read_root():
    return {"status": "Gateway Proxy is running via modular routers with LiteLLM integration"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
