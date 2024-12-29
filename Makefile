.PHONY: install dev run test clean docker-build docker-up docker-down

install:
	uv sync

dev:
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn src.app.main:app --host 0.0.0.0 --port 8000

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# Comandos Docker
docker-build:
	docker-compose build --no-cache

docker-build-cache:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -r {} +