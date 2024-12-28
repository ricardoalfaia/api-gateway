from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config.settings import settings
from src.app.services.proxy.service import ProxyService
from src.app.api.v1.gateway import router as gateway_router
from datetime import datetime
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    redirect_slashes=True
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    allow_credentials=True,
)

app.include_router(gateway_router, prefix=settings.API_V1_STR)

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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True
    )