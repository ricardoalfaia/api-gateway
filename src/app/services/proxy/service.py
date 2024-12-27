from fastapi import FastAPI, Request, HTTPException
import httpx
from typing import Any
from src.app.core.config.settings import settings

app = FastAPI()

class ProxyService:
    def __init__(self, services_config: Dict[str, Any]):
        self.services = services_config
    
    async def forward_request(
        self,
        service: str,
        path: str,
        request: Request
    ) -> Any:
        if service not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")
        
        service_config = self.services[service]
        target_url = f"{service_config.url}/{path}".rstrip("/")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                    content=await request.body(),
                    timeout=service_config.timeout
                )
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.json()
                }
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error forwarding request to service: {str(e)}"
            )

proxy_service = ProxyService(settings.services)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    return await proxy_service.forward_request(service, path, request)
