.PHONY: help install setup test lint format clean run

help:
	@echo "Virtual Council Assistant - Available Commands"
	@echo "=============================================="
	@echo "make install    - Install dependencies"
	@echo "make setup      - Initialize database and sample projects"
	@echo "make test       - Run tests"
	@echo "make lint       - Run linters (ruff)"
	@echo "make format     - Format code with black"
	@echo "make typecheck  - Run type checking with mypy"
	@echo "make clean      - Clean generated files"
	@echo "make run        - Run the application"

install:
	pip install -r requirements.txt

setup:
	python setup.py

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	ruff check app/ tests/

format:
	black app/ tests/

typecheck:
	mypy app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage

run:
	python -m app.main
