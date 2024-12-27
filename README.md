# E-commerce Gateway Service

Gateway service para microserviços do e-commerce utilizando FastAPI.

## Setup do Ambiente

# Criar ambiente virtual
```bash
uv venv
```

# Ativar ambiente
```bash
source .venv/bin/activate  # Linux/MacOS

# ou
# .venv\Scripts\activate  # Windows
```

# Instalar dependências

```bash
uv add "fastapi[all]"
uv add httpx
uv add python-dotenv
```

# Dependências de desenvolvimento
```bash
uv add -d pytest
uv add -d black
uv add -d ruff
uv add -d isort
```

## Estrutura do Projeto

```tree
projeto/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   └── dependencies/
│   │   ├── core/
│   │   │   ├── config/
│   │   │   └── security/
│   │   └── services/
│   │       └── proxy/
│   └── tests/
└── README.md
```

Ah, para criar essas visualizações de estrutura de diretórios no Markdown, você usa a formatação com três backticks (```) e identação com caracteres especiais. Vou te mostrar como:
markdownCopy# Estrutura padrão de diretórios


# Adiciona os arquivos e faz o primeiro commit
```bash
git add .
git commit -m "feat: initial project setup"
```	

# Define a branch principal como 'main'

```bash	
git branch -M main
```

## Rodar o projeto atraves do makeFile

```bash	
# Primeiro, instale o Chocolatey se ainda não tiver
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Depois instale o make
choco install make
```
