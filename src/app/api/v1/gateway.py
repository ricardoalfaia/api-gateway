from fastapi import APIRouter, Request, HTTPException
from src.app.core.config.settings import settings
from src.app.services.proxy.service import ProxyService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Configurando os serviços disponíveis
services_config = {
    name: {
        "url": service.url,
        "timeout": service.timeout
    } 
    for name, service in settings.services.items()
    if service.enabled
}

logger.info(f"Gateway router initialized with services: {services_config}")
proxy_service = ProxyService(services_config)

@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def forward_to_service(
    service: str,
    path: str = "",
    request: Request = None,
):
    """
    Forward requests to the appropriate service
    - service: name of the service to forward to
    - path: the remaining path after the service name
    - request: the original request object
    """
    logger.info(f"Received request - Method: {request.method}, Service: {service}, Path: {path}")
    logger.debug(f"Full URL: {request.url}")
    
    # Reconstruct complete path including query params
    full_path = path
    if request.query_params:
        full_path = f"{path}?{request.query_params}"
    
    try:
        return await proxy_service.forward_request(
            service=service,
            path=full_path,
            request=request
        )
        
    except HTTPException as e:
        logger.error(f"HTTP Exception in gateway: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in gateway: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Gateway Error")

@router.get("/health")
async def health_check():
    services_status = {
        name: {"url": service.url, "enabled": service.enabled}
        for name, service in settings.services.items()
    }
    logger.debug(f"Health check - services status: {services_status}")
    return {
        "status": "healthy",
        "services": services_status
    }