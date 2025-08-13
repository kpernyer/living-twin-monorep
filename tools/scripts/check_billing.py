#!/usr/bin/env python3
"""
check_billing.py - English-only
- Verifies OPENAI_API_KEY is set and valid
- Calls /v1/models
- Performs a minimal embeddings request (text-embedding-3-small)
"""

import os
import sys
from typing import Optional

# Dependency check
try:
    import requests
except ImportError:
    print("❌ Missing dependency: requests")
    print("   Install with: pip install requests")
    sys.exit(1)

API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY")
ORG_ID = os.environ.get("OPENAI_ORG_ID")  # optional


def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def headers():
    if not API_KEY:
        die("OPENAI_API_KEY is not set. Run:  source .env  or export it in your shell.")
    h = {"Authorization": f"Bearer {API_KEY}"}
    if ORG_ID:
        h["OpenAI-Organization"] = ORG_ID
    return h


def explain_error(status: int, body: dict | str) -> str:
    detail = ""
    if isinstance(body, dict):
        err = body.get("error") or {}
        if isinstance(err, dict):
            detail = f"{err.get('type','')} - {err.get('message','')}".strip()
    if not detail and isinstance(body, str):
        detail = body[:400]

    hints = []
    if status in (401, 403):
        hints += [
            "Check OPENAI_API_KEY (wrong/old/revoked).",
            "If you have multiple orgs: set OPENAI_ORG_ID=org_xxx.",
        ]
    elif status in (402, 429):
        hints += [
            "Likely billing/quota issue: set up Pay-as-you-go at platform.openai.com → Billing.",
            "Increase Monthly usage limit or soft limit if needed.",
        ]
    elif status >= 500:
        hints += ["Temporary API issue: try again shortly."]

    base = f"❌ HTTP {status}"
    if detail:
        base += f" — {detail}"
    if hints:
        base += "\n" + "\n".join(f"- {h}" for h in hints)
    return base


def http_json(path: str, method: str = "GET", payload: Optional[dict] = None):
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    try:
        resp = requests.request(method, url, headers=headers(), json=payload, timeout=20)
        ct = (resp.headers.get("Content-Type") or "").lower()
        body = resp.json() if "application/json" in ct else resp.text
        return resp.status_code, body
    except requests.exceptions.RequestException as e:
        die(f"❌ Network error: {e}")


def main():
    print("Checking /v1/models ...")
    status, body = http_json("/models")
    if status != 200:
        print(explain_error(status, body))
        sys.exit(2)

    # Print a small preview of model IDs
    data = body.get("data", []) if isinstance(body, dict) else []
    model_ids = [m.get("id") for m in data if isinstance(m, dict)]
    print(f"✅ OK — API reachable. Models: {len(model_ids)}")
    if model_ids:
        preview = ", ".join(model_ids[:8])
        print(f"   Example: {preview}")

    # Minimal embeddings call (cheap & confirms billing)
    print("\nChecking embeddings (text-embedding-3-small) ...")
    payload = {"model": "text-embedding-3-small", "input": "ping"}
    status, body = http_json("/embeddings", method="POST", payload=payload)
    if status == 200 and isinstance(body, dict) and "data" in body:
        dim = len(body["data"][0]["embedding"]) if body.get("data") else "?"
        print(f"✅ OK — embeddings work. Dimension: {dim} (Neo4j index should be 1536)")
        print("\nAll good! Billing/API access is functional.")
        sys.exit(0)
    else:
        print(explain_error(status, body))
        sys.exit(3)


if __name__ == "__main__":
    main()
