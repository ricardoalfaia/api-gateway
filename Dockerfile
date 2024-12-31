FROM python:3.12-slim

WORKDIR /app

# Install git and cleanup
RUN apt-get update && apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Clone repository
RUN git clone https://github.com/ricardoalfaia/api-gateway.git . 

RUN echo "PROJECT_NAME=${PROJECT_NAME:-'E-commerce Gateway'}" > .env && \
    echo "API_V1_STR=${API_V1_STR:-'/api/v1'}" >> .env && \
    echo "APP_ENV=${APP_ENV:-development}" >> .env && \
    echo "SERVICES__products=${SERVICES__products:-http://localhost:8001}" >> .env

# Install dependencies
RUN uv pip install --system uvicorn
RUN uv pip install --system .

# Define variável de ambiente
ENV APP_ENV=development

# Run application
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]