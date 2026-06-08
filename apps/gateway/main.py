import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # To import ee

from fastapi import FastAPI, Response
from routers import openai_proxy, anthropic_proxy, gemini_proxy, mcp_proxy
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    from ee.license import is_ee_active
    EE_ACTIVE = is_ee_active()
except ImportError:
    EE_ACTIVE = False

logger.info(f"--- Enterprise Edition Active: {EE_ACTIVE} ---")

app = FastAPI(title="ZeroTrust Agents Gateway Proxy")

# Include modular routers
app.include_router(openai_proxy.router)
app.include_router(anthropic_proxy.router)
app.include_router(gemini_proxy.router)
app.include_router(mcp_proxy.router)

@app.get("/")
def read_root():
    return {"status": "Gateway Proxy is running via modular routers with LiteLLM integration"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
