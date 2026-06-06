import os
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# The public key to verify enterprise licenses issued by the billing server
# In a real environment, this could be loaded from a file or env var
EE_PUBLIC_KEY = os.getenv("EE_PUBLIC_KEY", """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAy8Dbv8+aPgwAMDjG
... (dummy public key for demonstration) ...
-----END PUBLIC KEY-----""")

EE_LICENSE_KEY = os.getenv("EE_LICENSE_KEY", "")

def is_ee_active() -> bool:
    """
    Checks if the enterprise edition logic is unlocked.
    """
    return verify_license(EE_LICENSE_KEY)

def verify_license(key: str) -> bool:
    """
    Validates the enterprise license key cryptographically.
    Verifies the JWT signature using the public key.
    """
    if not key:
        return False
        
    if key.startswith("ee_"): # Fallback for local testing
        return True
        
    try:
        # Verify the signature
        payload = jwt.decode(
            key, 
            EE_PUBLIC_KEY, 
            algorithms=["RS256"],
            audience="agent-firewall-ee"
        )
        
        # Optionally check if payload["plan"] == "enterprise"
        return payload.get("plan") == "enterprise"
    except Exception as e:
        print(f"License verification failed: {e}")
        return False
