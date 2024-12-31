from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ipaddress import ip_address, ip_network
import logging

logger = logging.getLogger(__name__)

class InternalNetworkMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, internal_ranges):
        super().__init__(app)
        self.internal_ranges = [ip_network(cidr.strip()) for cidr in internal_ranges]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        logger.debug(f"Client IP: {client_ip}")
        
        if not any(ip_address(client_ip) in cidr for cidr in self.internal_ranges):
            logger.warning(f"Access denied for IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        return await call_next(request)
