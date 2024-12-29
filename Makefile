.PHONY: run dev test clean

run:
	uvicorn src.app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

install:
	uv sync

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete