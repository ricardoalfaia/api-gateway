from fastapi import FastAPI, Request
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config.settings import settings
from src.app.services.proxy.service import ProxyService
from src.app.api.v1.gateway import router as gateway_router
from src.app.core.security.middleware import InternalNetworkMiddleware
from datetime import datetime

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    redirect_slashes=True,
    debug=settings.performance.debug_mode,   
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    allow_credentials=True,
)


# Internal Network Middleware
if settings.internal_network:
    internal_ranges = settings.internal_network.ranges
    app.add_middleware(InternalNetworkMiddleware, internal_ranges=internal_ranges)


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

@app.get("/debug/services")
async def debug_services():
    return {
        name: {
            "url": service.url,
            "api_key": service.api_key,
            "enabled": service.enabled,
            "timeout": service.timeout
            # "mtls": service.mtls
        }
        for name, service in settings.services.items()
    }
    
@app.get("/api/v1/test")
async def test():
    return {
        "status": "ok",
        "message": "mTLS test endpoint"
    }
    
if __name__ == "__main__":
    # Configurar uvicorn com SSL/TLS
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        ssl_keyfile="certs/server.key",
        ssl_certfile="certs/server.crt",
        ssl_ca_certs="certs/ca.crt",
        ssl_cert_reqs=2  # ssl.CERT_REQUIRED
    )