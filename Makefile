# Tableau LangChain MCP Server - Development Makefile

.PHONY: help install install-dev test clean format lint setup check run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package and dependencies"
	@echo "  install-dev  - Install in development mode with dev dependencies"
	@echo "  test         - Run the test suite"
	@echo "  format       - Format code with black and isort"
	@echo "  lint         - Run linting with mypy"
	@echo "  setup        - Create .env file from template"
	@echo "  check        - Run configuration and dependency checks"
	@echo "  run          - Run the MCP server directly"
	@echo "  clean        - Remove build artifacts"

# Installation
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"
	pre-commit install

# Setup
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from template. Please edit it with your configuration."; \
	else \
		echo ".env file already exists. Use 'make setup-force' to overwrite."; \
	fi

setup-force:
	cp .env.example .env
	@echo "Overwrote .env file with template. Please edit it with your configuration."

# Testing and validation
test:
	python test_server.py

check: test

# Code quality
format:
	black tableau_langchain_mcp/
	isort tableau_langchain_mcp/

lint:
	mypy tableau_langchain_mcp/

# Running
run:
	python tableau_langchain_mcp/server.py

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build for distribution
build: clean format lint
	python -m build

# Quick development setup
dev-setup: install-dev setup
	@echo "Development environment setup complete!"
	@echo "1. Edit .env file with your Tableau and OpenAI credentials"
	@echo "2. Run 'make check' to validate your setup"
	@echo "3. Run 'make run' to start the server"
