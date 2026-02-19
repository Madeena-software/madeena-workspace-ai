.PHONY: help run test lint docker-build docker-run install clean

help:
	@echo "Madeena Core - Available Commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run mypy and bandit"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make clean         - Clean build artifacts"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir madeena_core

test:
	pytest madeena_core/tests/ -v --cov=madeena_core/app --cov-report=term-missing --cov-report=html

lint:
	@echo "Running mypy strict type checking..."
	mypy madeena_core/app --strict --ignore-missing-imports
	@echo "Running bandit security checks..."
	bandit -r madeena_core/app -ll

docker-build:
	docker build -t madeena-core:latest .

docker-run:
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage
