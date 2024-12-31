from fastapi import FastAPI, Request
import uvicorn
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return {
        "message": "Test service with mTLS",
        "client_cert": request.client.certificate,  # Informações do certificado do cliente
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/test")
async def test():
    return {
        "status": "ok",
        "message": "mTLS test endpoint"
    }

if __name__ == "__main__":
    # Configurar uvicorn com SSL/TLS
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        ssl_keyfile="certs/server.key",
        ssl_certfile="certs/server.crt",
        ssl_ca_certs="certs/ca.crt",
        ssl_cert_reqs=2  # ssl.CERT_REQUIRED
    )