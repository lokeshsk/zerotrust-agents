from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import policies, logs, auth, tenants, ws, integrations
import time

# Rely on Alembic for database migrations in production
# models.Base.metadata.create_all(bind=engine)

# Seed default tenant
from database import SessionLocal
db = SessionLocal()
if not db.query(models.TenantDB).filter(models.TenantDB.id == "default").first():
    default_tenant = models.TenantDB(id="default", name="Default Organization", api_key="sk-default")
    db.add(default_tenant)
    db.commit()
db.close()

app = FastAPI(title="ZeroTrust Agents Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modular route inclusion
app.include_router(policies.router)
app.include_router(logs.router)
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(ws.router)
app.include_router(integrations.router)

@app.get("/")
def read_root():
    return {"status": "Control Plane is running cleanly via modular routers."}
