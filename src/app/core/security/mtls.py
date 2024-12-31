from typing import Optional
import ssl
from pathlib import Path
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MTLSConfig:
    def __init__(
        self,
        cert_path: Path,
        key_path: Path,
        ca_path: Path
    ):
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        
    def create_ssl_context(self) -> ssl.SSLContext:
        try:
            context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=str(self.ca_path)
            )
            
            # Configurar certificado e chave do cliente
            context.load_cert_chain(
                certfile=str(self.cert_path),
                keyfile=str(self.key_path)
            )
            
            # Forçar verificação do certificado
            context.verify_mode = ssl.CERT_REQUIRED
            # Verificar hostname
            context.check_hostname = True
            
            return context
        except Exception as e:
            logger.error(f"Error creating SSL context: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize mTLS configuration"
            )