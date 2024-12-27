# src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config.settings import settings
from src.app.services.proxy.service import ProxyService
from src.app.api.v1 import gateway
from fastapi import APIRouter
from datetime import datetime

import httpx


router = APIRouter()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS - Agora usando a nova estrutura de configuração
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    allow_credentials=True,
)

app.include_router(gateway.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": "API Gateway",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Rotas

router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def forward_to_service(
    service: str,
    path: str,
    request: Request,
):
    response = await proxy_service.forward_request(service, path, request)
    return {
        "status_code": response["status_code"],
        "headers": response["headers"],
        "content": response["content"]
    }

