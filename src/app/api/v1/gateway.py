# src/app/api/v1/gateway.py
from fastapi import APIRouter, Request
from src.app.core.config.settings import settings
from src.app.services.proxy.service import ProxyService
from typing import Dict


router = APIRouter()

# Convertendo as configurações dos serviços para o formato esperado pelo ProxyService
services_config = {
    name: service.url 
    for name, service in settings.services.items()
    if service.enabled  # Só incluímos serviços habilitados
}

proxy_service = ProxyService(services_config)

@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def forward_to_service(
    service: str,
    path: str,
    request: Request,
):
    return await proxy_service.forward_request(service, path, request)

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            name: {"url": service.url, "enabled": service.enabled}
            for name, service in settings.services.items()
        }
    }