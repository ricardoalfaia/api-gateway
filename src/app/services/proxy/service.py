from typing import Dict, Any
from fastapi import Request, HTTPException, Response
import httpx
import logging
from urllib.parse import urljoin
from src.app.core.config.settings import settings

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProxyService:
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config
        logger.info(f"ProxyService initialized with config: {services_config}")

    def _build_target_url(self, service: str, path: str) -> str:
        """Build the target URL ensuring proper URL joining"""
        service_config = self.services[service]
        base_url = service_config['url'].rstrip('/')
        
        # Inicializa com a base da URL
        full_path = []
        
        # Adiciona o prefixo da API se ainda não estiver no path
        if not path.startswith(settings.API_V1_STR):
            full_path.append(settings.API_V1_STR.strip('/'))
            
        # Adiciona o nome do serviço se ainda não estiver no path
        if not path.startswith(f"/{service}") and service not in path:
            full_path.append(service)
            
        # Adiciona o resto do path, removendo barras duplicadas
        clean_path = path.strip('/')
        if clean_path and clean_path != service:
            if clean_path.startswith(settings.API_V1_STR.strip('/')):
                clean_path = clean_path[len(settings.API_V1_STR.strip('/')):]
            if clean_path.startswith(service):
                clean_path = clean_path[len(service):]
            clean_path = clean_path.strip('/')
            if clean_path:
                full_path.append(clean_path)
        
        # Junta todos os componentes do path
        final_path = '/'.join(full_path)
        target_url = f"{base_url}/{final_path}"
        
        logger.debug(f"URL Construction:")
        logger.debug(f"  Base URL: {base_url}")
        logger.debug(f"  Original Path: {path}")
        logger.debug(f"  Final Path: {final_path}")
        logger.debug(f"  Target URL: {target_url}")
        
        return target_url

    async def forward_request(
        self,
        service: str,
        path: str,
        request: Request
    ) -> Response:
        """Forward the request to the target service"""
        logger.debug(f"Forwarding request - Service: {service}, Path: {path}")
        logger.debug(f"Original request URL: {request.url}")
        logger.debug(f"Method: {request.method}")
        
        if service not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")

        target_url = self._build_target_url(service, path)
        
        # Prepare headers - remove problematic ones
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        try:
            body = await request.body()
            logger.debug(f"Request body size: {len(body)} bytes")
            logger.debug(f"Making request to: {target_url}")
            logger.debug(f"Headers: {headers}")
            
            # Get query parameters
            params = dict(request.query_params)
            logger.debug(f"Query params: {params}")

            timeout = httpx.Timeout(30.0)
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout,
                verify=False  # Desativa verificação SSL para desenvolvimento
            ) as client:
                # Send request to target service
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=params,
                    content=body
                )
                
                logger.info(f"Response received - Status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get('content-type')
                )

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {str(e)}")
            raise HTTPException(status_code=504, detail="Gateway Timeout")
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(status_code=502, detail=str(e))
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))