from fastapi import Request, HTTPException
import httpx
from typing import Any, Dict

class ProxyService:
    def __init__(self, services_config: Dict[str, str]):
        self.services = services_config
    
    async def forward_request(
        self,
        service: str,
        path: str,
        request: Request
    ) -> Any:
        """
        Encaminha a requisição para o serviço apropriado
        """
        if service not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service} not found")
        
        service_url = self.services[service]
        target_url = f"{service_url}/{path}"
        
        # Remove leading slash if present
        target_url = target_url.replace("//", "/")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                    content=await request.body(),
                    timeout=30.0
                )
                
                return response.json()
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error forwarding request to service: {str(e)}"
            )