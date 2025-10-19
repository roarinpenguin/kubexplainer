# Kubernetes YAML Explainer - Makefile

.PHONY: help build start stop restart logs clean test dev-backend dev-frontend

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

start: ## Start the application
	docker-compose up -d
	@echo "Application started at http://localhost:8080"

stop: ## Stop the application
	docker-compose down

restart: ## Restart the application
	docker-compose restart

logs: ## View application logs
	docker-compose logs -f

clean: ## Stop and remove all containers, volumes, and images
	docker-compose down -v --rmi all

dev-backend: ## Run backend in development mode
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt && python main.py

dev-frontend: ## Run frontend in development mode
	cd frontend && npm install && npm start

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

test: ## Run tests (placeholder)
	@echo "Tests not yet implemented"

status: ## Check application status
	docker-compose ps

shell: ## Open a shell in the running container
	docker-compose exec app /bin/sh

db-reset: ## Reset the database (removes all data!)
	docker-compose down -v
	docker-compose up -d
	@echo "Database reset complete"
