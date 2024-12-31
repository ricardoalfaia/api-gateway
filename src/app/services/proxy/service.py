from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, Response
import httpx
import logging
from pathlib import Path
import ssl
from src.app.core.config.settings import settings, ServiceConfig
from src.app.core.security.mtls import MTLSConfig

logger = logging.getLogger(__name__)

class ProxyService:
    def __init__(self, services_config: Dict[str, Dict[str, Any]]):
        # Convertendo cada configuração para ServiceConfig
        self.services: Dict[str, ServiceConfig] = {}
        self.mtls_config: Optional[MTLSConfig] = None

        # Inicializar mTLS se configurado
        self._setup_mtls()

        for service_name, config in services_config.items():
            try:
                self.services[service_name] = ServiceConfig(
                    url=config['url'],
                    api_key=config.get('api_key'),
                    timeout=config.get('timeout', 30),
                    enabled=config.get('enabled', True),
                    require_mtls=config.get('require_mtls', False)
                )
                logger.debug(f"Initialized service {service_name} with config: {config}")
            except Exception as e:
                logger.error(f"Error initializing service {service_name}: {e}")
                raise

    def _setup_mtls(self) -> None:
        """Configura mTLS se os certificados estiverem disponíveis"""
        try:
            # Verifica se mTLS está habilitado nas configurações
            if not settings.mtls.enabled:  # Mudança aqui: acessando diretamente o atributo
                logger.info("mTLS is not enabled in settings")
                return

            cert_path = Path(settings.mtls.cert_path)
            key_path = Path(settings.mtls.key_path)
            ca_path = Path(settings.mtls.ca_path)

            # Verifica se todos os arquivos necessários existem
            if all(p.exists() for p in [cert_path, key_path, ca_path]):
                self.mtls_config = MTLSConfig(
                    cert_path=cert_path,
                    key_path=key_path,
                    ca_path=ca_path
                )
                logger.info("mTLS configuration loaded successfully")
            else:
                logger.warning("mTLS certificates not found, running without mTLS")
        except Exception as e:
            logger.error(f"Error setting up mTLS: {e}")
        

    def _build_target_url(self, service: str, path: str) -> str:
        service_config = self.services[service]
        base_url = service_config.url.rstrip('/')
        
        full_path = []
        
        if not path.startswith(settings.API_V1_STR):
            full_path.append(settings.API_V1_STR.strip('/'))
            
        if not path.startswith(f"/{service}") and service not in path:
            full_path.append(service)
            
        clean_path = path.strip('/')
        if clean_path and clean_path != service:
            if clean_path.startswith(settings.API_V1_STR.strip('/')):
                clean_path = clean_path[len(settings.API_V1_STR.strip('/')):]
            if clean_path.startswith(service):
                clean_path = clean_path[len(service):]
            clean_path = clean_path.strip('/')
            if clean_path:
                full_path.append(clean_path)
        
        final_path = '/'.join(full_path)
        target_url = f"{base_url}/{final_path}"
        
        logger.debug(f"Built target URL: {target_url} for service: {service}")
        return target_url
    
    def _get_client_config(self, service_config: ServiceConfig) -> Dict[str, Any]:
        """Prepara a configuração do cliente HTTP com ou sem mTLS"""
        client_config = {
            "follow_redirects": True,
            "timeout": httpx.Timeout(service_config.timeout),
        }

        # Adiciona configuração mTLS se necessário
        if service_config.require_mtls and self.mtls_config:
            try:
                ssl_context = self.mtls_config.create_ssl_context()
                client_config.update({
                    "verify": str(self.mtls_config.ca_path),
                    "cert": (
                        str(self.mtls_config.cert_path),
                        str(self.mtls_config.key_path)
                    )
                })
                logger.debug(f"mTLS configuration added for request")
            except Exception as e:
                logger.error(f"Error configuring mTLS for request: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to configure secure connection"
                )
        else:
            client_config["verify"] = False

        return client_config

    async def forward_request(
        self,
        service: str,
        path: str,
        request: Request,
    ) -> Response:
        if service not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")

        service_config = self.services[service]
        logger.debug(f"Processing request for service: {service}")
        logger.debug(f"Service config: {service_config}")

        # Verifica se o serviço requer mTLS e se está configurado
        if service_config.require_mtls and not self.mtls_config:
            logger.error(f"Service {service} requires mTLS but it's not configured")
            raise HTTPException(
                status_code=500,
                detail="Service requires secure connection but it's not configured"
            )

        target_url = self._build_target_url(service, path)
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)

        # Adiciona a API key se existir
        if service_config.api_key:
            headers['X-API-Key'] = service_config.api_key
            logger.debug(f"Added X-API-Key header for service {service}")
        
        logger.debug(f"Final headers: {headers}")

        try:
            body = await request.body()
            params = dict(request.query_params)

            # Obter configuração do cliente antes de usar
            client_config = self._get_client_config(service_config)  

            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=httpx.Timeout(service_config.timeout),
                verify=False
            ) as client:
                
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=params,
                    content=body
                )
                
                logger.info(f"Response from {service}: {response.status_code}")
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get('content-type')
                )

        except Exception as e:
            logger.error(f"Error forwarding request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))