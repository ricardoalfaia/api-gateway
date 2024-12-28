from typing import Dict, Any
from fastapi import Request, HTTPException, Response
import httpx
import logging
from urllib.parse import urljoin, urlparse, parse_qs
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
        
        # Clean the path
        clean_path = path.strip()
        
        # Remove API prefix if present
        if clean_path.startswith(settings.API_V1_STR):
            clean_path = clean_path[len(settings.API_V1_STR):].lstrip('/')
            
        # Remove service name from start of path if present
        if clean_path.startswith(f"{service}/"):
            clean_path = clean_path[len(service)+1:]
        elif clean_path == service:
            clean_path = ""
            
        # Ensure path starts with slash if not empty
        if clean_path and not clean_path.startswith('/'):
            clean_path = f"/{clean_path}"
        elif not clean_path:
            clean_path = "/"
            
        # Construct final URL
        target_url = f"{base_url}{clean_path}"
        
        logger.debug(f"URL Construction:")
        logger.debug(f"  Base URL: {base_url}")
        logger.debug(f"  Original Path: {path}")
        logger.debug(f"  Clean Path: {clean_path}")
        logger.debug(f"  Final URL: {target_url}")
        
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

            timeout = httpx.Timeout(30.0)
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout
            ) as client:
                # Send request to target service
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
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