# Use uma imagem base do Python 3.12.4 slim
FROM python:3.12.4-slim

# Defina variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_NO_COLOR=1

# Instale as dependências do sistema incluindo make
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho
WORKDIR /app

# Clone o repositório
RUN git clone https://github.com/ricardoalfaia/api-gateway.git .

# Copie o Makefile e o .env
COPY Makefile .
COPY .env .

# Instale o uv
RUN pip install uv

# Use o Makefile para instalar dependências e configurar o ambiente
RUN make install

# Comando para executar a aplicação usando o Makefile
CMD ["make", "run"]

EXPOSE 8000