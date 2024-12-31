# src/app/core/security/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ipaddress import ip_address, ip_network

class InternalNetworkMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        internal_ranges = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
        
        if not any(ip_address(client_ip) in ip_network(cidr) for cidr in internal_ranges):
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        return await call_next(request)