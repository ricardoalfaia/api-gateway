# src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config.settings import settings
from datetime import datetime
import httpx

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
from src.app.api.v1 import gateway
app.include_router(gateway.router, prefix=settings.API_V1_STR)