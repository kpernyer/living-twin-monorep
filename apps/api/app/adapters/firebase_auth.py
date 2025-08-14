import os
from typing import Dict
from ..ports.authz import UserContext

# Support both FIREBASE_PROJECT_ID and legacy PROJECT_ID
PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID") or os.getenv("PROJECT_ID")
AUTH_EMULATOR = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")

class FirebaseAuth:
    def __init__(self, bypass: bool = False):
        self.bypass = bypass

    def verify(self, bearer: str) -> UserContext:
        if self.bypass:
            return {"uid": "dev-user", "tenantId": "demo", "role": "owner", "claims": {}}
        if not bearer or not bearer.startswith("Bearer "):
            raise ValueError("Missing Bearer token")
        token = bearer.split(" ", 1)[1]
        # If using emulator, tokens are unsigned debug tokens; trust minimal structure
        if AUTH_EMULATOR:
            decoded = {"uid": "emulator-user", "tenantId": "demo", "role": "owner", "claims": {}}
        else:
            try:
                import firebase_admin
                from firebase_admin import auth as fb_auth
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                decoded = fb_auth.verify_id_token(token, check_revoked=True)
            except Exception:
                from google.oauth2 import id_token
                from google.auth.transport import requests
                decoded = id_token.verify_firebase_token(token, requests.Request(), audience=PROJECT_ID)
        tenant_id = decoded.get("tenantId") or decoded.get("claims", {}).get("tenantId")
        role = decoded.get("role") or decoded.get("claims", {}).get("role", "viewer")
        if not tenant_id:
            raise ValueError("Missing tenantId claim")
        return {"uid": decoded.get("uid"), "tenantId": tenant_id, "role": role, "claims": decoded}

class SimpleAuthorizer:
    def can_cross_tenant(self, user: UserContext, target_tenant: str) -> bool:
        return user["role"] in ("owner",) and user["tenantId"] != target_tenant
