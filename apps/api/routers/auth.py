from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import jwt
from jwt import PyJWKClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import models
from database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

# Secret key for simple JWT simulation
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is missing. It is required for security.")

# Application URL
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/" if AUTH0_DOMAIN else None

jwks_client = PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json") if AUTH0_DOMAIN else None
security = HTTPBearer(auto_error=False)

class SetupRequest(BaseModel):
    password: str

class LoginRequest(BaseModel):
    password: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")
        
    token = credentials.credentials
    
    # If no Auth0 domain is configured, fallback to basic decode or master key check
    if not AUTH0_DOMAIN or not jwks_client:
        try:
            # Fallback for local development if Auth0 is not configured
            # Assume local token is just the raw hash or a mock payload
            if len(token) == 64: # basic hash
                return {"tenant_id": "default", "user_id": "admin"}
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid local token")
            
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUTH0_API_AUDIENCE,
            issuer=AUTH0_ISSUER,
        )
        return payload
    except jwt.exceptions.PyJWKClientError as error:
        raise HTTPException(status_code=401, detail=f"JWKS Error: {str(error)}")
    except jwt.exceptions.DecodeError as error:
        raise HTTPException(status_code=401, detail=f"Decode Error: {str(error)}")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as error:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(error)}")

from fastapi import Header
def verify_gateway(x_gateway_secret: str = Header(default=None)):
    if x_gateway_secret != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid Gateway Secret")
    return True

def seed_default_permissions(db: Session):
    # Seed predefined roles and their permissions if they don't exist
    defaults = {
        "owner": ["policies:read", "policies:write", "logs:read", "billing:read", "billing:write", "settings:write"],
        "admin": ["policies:read", "policies:write", "logs:read", "settings:write"],
        "developer": ["policies:read", "logs:read"],
        "auditor": ["logs:read", "policies:read"]
    }
    
    if db.query(models.PermissionDB).count() == 0:
        for role, perms in defaults.items():
            for perm in perms:
                db.add(models.PermissionDB(role=role, permission=perm))
        db.commit()

def require_permission(required_perm: str):
    def permission_checker(
        x_tenant_id: str = Header(default="default", alias="x-tenant-id"),
        jwt_payload: dict = Depends(verify_jwt),
        db: Session = Depends(get_db)
    ):
        seed_default_permissions(db) # Ensure seed runs
        user_id = jwt_payload.get("user_id") or jwt_payload.get("sub")
        if not user_id:
            # If the user is an admin from master key (fallback)
            if jwt_payload.get("tenant_id") == "default":
                return True
            raise HTTPException(status_code=401, detail="Invalid user in token")
            
        role_binding = db.query(models.RoleBindingDB).filter(
            models.RoleBindingDB.user_id == user_id,
            models.RoleBindingDB.tenant_id == x_tenant_id
        ).first()
        
        if not role_binding:
            raise HTTPException(status_code=403, detail="User does not have access to this tenant")
            
        # Check permissions explicitly
        has_perm = db.query(models.PermissionDB).filter(
            models.PermissionDB.role == role_binding.role,
            models.PermissionDB.permission == required_perm
        ).first()
        
        if not has_perm:
            raise HTTPException(status_code=403, detail=f"Requires {required_perm} permission")
            
        return role_binding
    return permission_checker

@router.get("/setup-status")
def setup_status(db: Session = Depends(get_db)):
    admin = db.query(models.AdminDB).first()
    return {"is_setup": admin is not None}

@router.post("/setup")
def setup_admin(request: SetupRequest, db: Session = Depends(get_db)):
    admin = db.query(models.AdminDB).first()
    if admin:
        raise HTTPException(status_code=400, detail="Admin already setup")
    
    new_admin = models.AdminDB(
        username="admin",
        password_hash=hash_password(request.password)
    )
    db.add(new_admin)
    db.commit()
    return {"status": "success"}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    from main import EE_ACTIVE
    if EE_ACTIVE and AUTH0_DOMAIN:
        raise HTTPException(status_code=403, detail="Enterprise Edition is active. Please use SSO (/login/sso) to authenticate.")
        
    admin = db.query(models.AdminDB).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Admin not setup")
        
    if not verify_password(request.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
        
    # Return a basic token for demonstration
    # In production, use standard JWT with expiration
    # We use a hash here to simulate a token for the existing MVP, 
    # but normally this should be a properly signed JWT.
    import hashlib
    token = hashlib.sha256(f"{admin.username}:{SECRET_KEY}".encode()).hexdigest()
    return {"token": token}
@router.get("/login/sso")
def login_sso():
    if not AUTH0_DOMAIN:
        raise HTTPException(status_code=400, detail="Auth0 not configured")
    
    client_id = os.getenv("AUTH0_CLIENT_ID")
    redirect_uri = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8001/auth/callback")
    
    url = (
        f"https://{AUTH0_DOMAIN}/authorize"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid profile email"
        f"&audience={AUTH0_API_AUDIENCE or ''}"
    )
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)

import httpx
from fastapi.responses import RedirectResponse

@router.get("/callback")
async def auth_callback(code: str, db: Session = Depends(get_db)):
    if not AUTH0_DOMAIN:
        raise HTTPException(status_code=400, detail="Auth0 not configured")

    client_id = os.getenv("AUTH0_CLIENT_ID")
    client_secret = os.getenv("AUTH0_CLIENT_SECRET")
    redirect_uri = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8001/auth/callback")

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to exchange token")
        
        tokens = token_res.json()
        access_token = tokens.get("access_token")
        id_token = tokens.get("id_token")
        
        if id_token:
            decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
            sub = decoded_id_token.get("sub")
            email = decoded_id_token.get("email")

            if sub and email:
                user = db.query(models.UserDB).filter(models.UserDB.id == sub).first()
                if not user:
                    user = models.UserDB(id=sub, email=email)
                    db.add(user)
                    
                    tenant = db.query(models.TenantDB).filter(models.TenantDB.id == "default").first()
                    if not tenant:
                        tenant = models.TenantDB(id="default", name="Default Tenant", api_key="sk-default")
                        db.add(tenant)
                        db.commit()
                        
                    role_binding = models.RoleBindingDB(user_id=sub, tenant_id="default", role="owner")
                    db.add(role_binding)
                    db.commit()

        # Redirect back to the frontend with the access_token
        return RedirectResponse(url=f"{APP_URL}/?token={access_token}")

@router.get("/logout")
def logout():
    if not AUTH0_DOMAIN:
        # Fallback for basic auth just redirect to home
        return RedirectResponse(url=f"{APP_URL}/")
        
    client_id = os.getenv("AUTH0_CLIENT_ID")
    return_to = f"{APP_URL}/"
    url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={client_id}&returnTo={return_to}"
    return RedirectResponse(url)
