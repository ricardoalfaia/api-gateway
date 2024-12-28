# E-commerce Gateway Service

Gateway service para microserviços do e-commerce utilizando FastAPI.

## Descrição

API Gateway responsável por rotear requisições entre diferentes microserviços do ecossistema e-commerce. Implementa:
- Roteamento dinâmico
- Logging configurável
- Configurações por ambiente
- Proxy reverso para microserviços

## Requisitos

- Python 3.12+
- uv (gerenciador de pacotes e ambientes virtuais)
- make (opcional, para comandos automatizados)

## Setup do Ambiente

### Criar ambiente virtual
```bash
uv venv
```

### Ativar ambiente
```bash
source .venv/bin/activate  # Linux/MacOS
# ou
.venv\Scripts\activate  # Windows
```

### Instalar dependências
```bash
# Dependências principais
uv add "fastapi[all]"
uv add httpx
uv add python-dotenv
uv add pyyaml
uv add pydantic-settings

# Dependências de desenvolvimento
uv add -d pytest
uv add -d black
uv add -d ruff
uv add -d isort
```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto:
```env
APP_ENV=development  # ou production
```

2. As configurações específicas de ambiente estão em `src/app/core/config/environments/`:
- `base.yaml`: Configurações base
- `development.yaml`: Configurações de desenvolvimento
- `production.yaml`: Configurações de produção

## Executando o Projeto

### Diretamente com uvicorn
```bash	
uvicorn src.app.main:app --reload --port 8000
```

### Usando make
```bash
# Desenvolvimento
make dev

# Produção
make run
```

## Estrutura do Projeto

```
api-gateway/
├── src/
│   └── app/
│       ├── api/                  # Endpoints e rotas
│       │   ├── dependencies/     # Dependências compartilhadas
│       │   └── v1/              # Versão 1 da API
│       ├── core/                 # Core do sistema
│       │   ├── config/          # Configurações
│       │   └── security/        # Segurança
│       └── services/            # Serviços internos
│           └── proxy/           # Serviço de proxy
├── .env                         # Variáveis de ambiente
├── .gitignore
├── pyproject.toml              # Configuração do projeto
├── Makefile                    # Comandos automatizados
└── README.md
```

## Instalando make no Windows

```bash	
# Primeiro, instale o Chocolatey se ainda não tiver
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Depois instale o make
choco install make
```

## Endpoints Disponíveis

### Serviço de Produtos
- GET /api/v1/products/ - Lista todos os produtos
- GET /api/v1/products/{id} - Obtém um produto específico
- POST /api/v1/products/ - Cria um novo produto
- PUT /api/v1/products/{id} - Atualiza um produto
- DELETE /api/v1/products/{id} - Remove um produto

### Serviço de Pedidos
- GET /api/v1/orders/ - Lista todos os pedidos
- GET /api/v1/orders/{id} - Obtém um pedido específico
- POST /api/v1/orders/ - Cria um novo pedido
- PATCH /api/v1/orders/{id}/status - Atualiza o status de um pedido
- DELETE /api/v1/orders/{id} - Remove um pedido

### Endpoints do Gateway
- GET / - Informações sobre o gateway
- GET /health - Status de saúde do gateway

## Logs e Monitoramento

O sistema utiliza níveis de log configuráveis:
- DEBUG: Informações detalhadas (desenvolvimento)
- INFO: Informações gerais (produção)
- WARNING: Avisos
- ERROR: Erros que não quebram a aplicação
- CRITICAL: Erros graves

Configure o nível de log em `environments/{ambiente}.yaml`.

## Desenvolvimento

### Comandos make disponíveis
```bash
make dev      # Inicia em modo desenvolvimento
make run      # Inicia em modo produção
make test     # Roda os testes
make lint     # Verifica o código
make format   # Formata o código
make clean    # Limpa arquivos temporários
```

### Git Workflow
```bash
# Cria e muda para uma nova branch
git checkout -b feature/nome-da-feature

# Adiciona e comita alterações
git add .
git commit -m "feat: descrição da feature"

# Push para o repositório
git push origin feature/nome-da-feature
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.