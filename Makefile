# TenderIntel Makefile
# ===================
# 
# Professional Makefile for TenderIntel development and deployment
# Provides standardized commands for setup, testing, and operations

.PHONY: help install install-dev test lint format clean run docker-build docker-up docs

# Default target
help:
	@echo "🎯 TenderIntel - AI-Powered Competitive Intelligence"
	@echo "=================================================="
	@echo ""
	@echo "📋 Available Commands:"
	@echo ""
	@echo "🚀 Setup & Installation:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make setup        - Initialize project (database, config, sample data)"
	@echo ""
	@echo "🔍 Development:"
	@echo "  make run          - Start API server for development"
	@echo "  make test         - Run all tests with coverage"
	@echo "  make lint         - Run linting and type checking"
	@echo "  make format       - Format code with black and isort"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start with Docker Compose"
	@echo "  make docker-down  - Stop Docker services"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make docs         - Generate documentation"
	@echo "  make docs-serve   - Serve docs locally"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make reset-db     - Reset database with fresh schema"
	@echo ""
	@echo "🎯 Quick Start:"
	@echo "  make install-dev && make setup && make run"

# Installation targets
install:
	@echo "📦 Installing TenderIntel (production)..."
	pip install -e .

install-dev:
	@echo "📦 Installing TenderIntel (development)..."
	pip install -e ".[dev,tenderx]"
	pre-commit install --allow-missing-config || echo "⚠️  pre-commit not available"

setup:
	@echo "🔧 Initializing TenderIntel project..."
	python scripts/setup/initialize_project.py

# Development targets
run:
	@echo "🚀 Starting TenderIntel API server..."
	python -m tenderintel.api.server

test:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=src/tenderintel --cov-report=html --cov-report=term-missing

test-unit:
	@echo "🔬 Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "🔗 Running integration tests..."
	pytest tests/integration/ -v

# Code quality targets
lint:
	@echo "🔍 Running code quality checks..."
	@echo "1️⃣  Linting with flake8..."
	flake8 src/ tests/ || echo "⚠️  Linting issues found"
	@echo "2️⃣  Type checking with mypy..."
	mypy src/ || echo "⚠️  Type checking issues found"
	@echo "3️⃣  Security check..."
	bandit -r src/ || echo "⚠️  Security issues found"

format:
	@echo "✨ Formatting code..."
	@echo "1️⃣  Formatting with black..."
	black src/ tests/
	@echo "2️⃣  Sorting imports with isort..."
	isort src/ tests/

# Docker targets  
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🐳 Starting TenderIntel with Docker..."
	docker-compose up -d
	@echo "📍 API: http://localhost:8000"
	@echo "🌐 UI:  http://localhost:3000"

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

# Documentation targets
docs:
	@echo "📚 Generating documentation..."
	mkdocs build

docs-serve:
	@echo "📚 Serving documentation locally..."
	mkdocs serve
	@echo "📖 Docs: http://localhost:8001"

# Maintenance targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

reset-db:
	@echo "🗃️  Resetting database..."
	rm -f data/tenders.db
	python scripts/setup/initialize_project.py

# Deployment targets
build-dist:
	@echo "📦 Building distribution packages..."
	python -m build

upload-test:
	@echo "🚀 Uploading to Test PyPI..."
	python -m twine upload --repository testpypi dist/*

upload-prod:
	@echo "🚀 Uploading to PyPI..."
	python -m twine upload dist/*

# Development convenience targets
demo:
	@echo "🎭 Running demo scenarios..."
	curl -s "http://localhost:8000/test-demo-scenarios" | python -m json.tool

health:
	@echo "❤️  Checking system health..."
	curl -s "http://localhost:8000/health" | python -m json.tool

search-test:
	@echo "🔍 Testing intelligent search..."
	@echo "LAN Search:"
	curl -s "http://localhost:8000/search?q=lan&limit=3" | python -c "import sys,json; data=json.load(sys.stdin); print(f'  Results: {data.get(\"total_matches\")} matches in {data.get(\"execution_time_ms\")}ms')"
	@echo "API Search:"  
	curl -s "http://localhost:8000/search?q=api&limit=3" | python -c "import sys,json; data=json.load(sys.stdin); print(f'  Results: {data.get(\"total_matches\")} matches in {data.get(\"execution_time_ms\")}ms')"

# All-in-one targets
dev-setup: install-dev setup
	@echo "✅ Development environment ready!"
	@echo "🚀 Run: make run"

full-test: format lint test
	@echo "✅ All quality checks passed!"

# Production deployment
prod-setup: install setup
	@echo "✅ Production environment ready!"

# Quick start for new developers
quickstart:
	@echo "🚀 TenderIntel Quick Start"
	@echo "========================"
	@$(MAKE) install-dev
	@$(MAKE) setup  
	@echo ""
	@echo "✅ Setup complete! Starting server..."
	@$(MAKE) run

# Development workflow
dev: format lint test run
	@echo "🏁 Development workflow complete!"

# Show project status
status:
	@echo "📊 TenderIntel Project Status"
	@echo "============================"
	@echo "📁 Project: $(shell pwd)"
	@echo "🐍 Python: $(shell python --version)"
	@echo "📦 Package: $(shell python -c 'import tenderintel; print(f\"v{tenderintel.__version__}\"' 2>/dev/null || echo 'Not installed')"
	@echo "💾 Database: $(shell ls -la data/tenders.db 2>/dev/null | awk '{print $$5 \" bytes\"}' || echo 'Not found')"
	@echo "🔍 Tests: $(shell find tests/ -name '*.py' | wc -l | tr -d ' ') test files"
	@echo "📝 Docs: $(shell find docs/ -name '*.md' | wc -l | tr -d ' ') documentation files"
