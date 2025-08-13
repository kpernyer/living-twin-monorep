#!/usr/bin/env python3
"""
Set Firebase custom claims for a user (tenantId, role).
Usage:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
  python tools/scripts/set_claims.py <uid> <tenantId> <role>
"""
import os, sys
import firebase_admin
from firebase_admin import auth, credentials

def main():
    if len(sys.argv) != 4:
        print("Usage: set_claims.py <uid> <tenantId> <role>")
        sys.exit(1)
    uid, tenant, role = sys.argv[1:4]

    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    auth.set_custom_user_claims(uid, {"tenantId": tenant, "role": role})
    print(f"Set claims for uid={uid}: tenantId={tenant}, role={role}")

if __name__ == "__main__":
    main()
