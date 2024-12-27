.PHONY: dev test lint

# Rodar o servidor de desenvolvimento
dev:
	uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# Rodar os testes
test:
	pytest

# Formatar e verificar o código
lint:
	black .
	isort .
	ruff check .

# Instalar dependências de desenvolvimento
install-dev:
	uv add "fastapi[all]" httpx python-dotenv pydantic-settings
	uv add -d pytest black isort ruff

# Limpar arquivos Python compilados
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete