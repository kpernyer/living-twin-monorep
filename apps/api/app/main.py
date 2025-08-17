from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import load_config
from .di import init_container, container
from .routers import health, rag, intelligence

app = FastAPI(title="Twin API (Firebase-ready)")
cfg = load_config()
init_container(cfg)

if cfg.allow_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if cfg.bypass_auth or request.url.path in ("/healthz","/readyz"):
        request.state.user = {"uid":"dev","tenantId":"demo","role":"owner","claims":{}}
        return await call_next(request)
    try:
        token = request.headers.get("Authorization","")
        user = container.auth.verify(token)
        request.state.user = user
        return await call_next(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

app.include_router(health.router)
app.include_router(rag.router)
app.include_router(intelligence.router)
