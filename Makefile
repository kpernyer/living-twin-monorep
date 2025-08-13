# =========================
# Living Twin Monorepo - Makefile
# =========================

.PHONY: help dev staging prod check-costs check-resources terraform-init terraform-plan terraform-apply terraform-destroy docker-build docker-up docker-down

# Default target
help:
	@echo "🚀 Living Twin Monorepo Commands"
	@echo "================================"
	@echo ""
	@echo "📊 Cost & Resource Management:"
	@echo "  check-costs ENV=dev PROJECT=your-project    Check resource costs and utilization"
	@echo "  check-resources ENV=dev PROJECT=your-project Show scaling configuration"
	@echo ""
	@echo "🏗️  Infrastructure (Terraform):"
	@echo "  terraform-init                              Initialize Terraform"
	@echo "  terraform-plan ENV=dev PROJECT=your-project Plan infrastructure changes"
	@echo "  terraform-apply ENV=dev PROJECT=your-project Apply infrastructure changes"
	@echo "  terraform-destroy ENV=dev PROJECT=your-project Destroy infrastructure"
	@echo ""
	@echo "🐳 Local Development (Docker):"
	@echo "  docker-build                                Build all containers"
	@echo "  docker-up                                   Start local development environment"
	@echo "  docker-down                                 Stop local development environment"
	@echo ""
	@echo "🔧 Development Tools:"
	@echo "  seed-db                                     Seed local databases with test data"
	@echo "  api-dev                                     Run API in development mode"
	@echo "  web-dev                                     Run admin web in development mode"
	@echo ""
	@echo "📝 Examples:"
	@echo "  make check-costs ENV=dev PROJECT=my-living-twin-project"
	@echo "  make terraform-plan ENV=staging PROJECT=my-living-twin-project"
	@echo "  make docker-up"

# =========================
# Cost & Resource Management
# =========================

check-costs:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make check-costs ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make check-costs ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "🔍 Checking costs and resource utilization for $(ENV) environment..."
	python tools/scripts/check_resource_utilization.py --project-id $(PROJECT) --environment $(ENV)

check-resources:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make check-resources ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make check-resources ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "⚙️  Showing scaling configuration for $(ENV) environment..."
	python tools/scripts/check_resource_utilization.py --project-id $(PROJECT) --environment $(ENV) --show-config

# =========================
# Terraform Infrastructure
# =========================

terraform-init:
	@echo "🏗️  Initializing Terraform..."
	cd packages/gcp_firebase/terraform && terraform init

terraform-plan:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make terraform-plan ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make terraform-plan ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "📋 Planning Terraform changes for $(ENV) environment..."
	cd packages/gcp_firebase/terraform && \
	terraform workspace select $(ENV) || terraform workspace new $(ENV) && \
	terraform plan -var="project_id=$(PROJECT)" -var-file=environments/$(ENV).tfvars

terraform-apply:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make terraform-apply ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make terraform-apply ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "🚀 Applying Terraform changes for $(ENV) environment..."
	@echo "⚠️  This will create/modify cloud resources and may incur costs!"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	cd packages/gcp_firebase/terraform && \
	terraform workspace select $(ENV) || terraform workspace new $(ENV) && \
	terraform apply -var="project_id=$(PROJECT)" -var-file=environments/$(ENV).tfvars

terraform-destroy:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make terraform-destroy ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make terraform-destroy ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "💥 Destroying Terraform infrastructure for $(ENV) environment..."
	@echo "⚠️  This will DELETE all cloud resources! This action cannot be undone!"
	@read -p "Are you absolutely sure? Type 'destroy' to confirm: " confirm && [ "$$confirm" = "destroy" ] || exit 1
	cd packages/gcp_firebase/terraform && \
	terraform workspace select $(ENV) && \
	terraform destroy -var="project_id=$(PROJECT)" -var-file=environments/$(ENV).tfvars

# =========================
# Docker Development
# =========================

docker-build:
	@echo "🐳 Building Docker containers..."
	docker-compose build

docker-up:
	@echo "🚀 Starting local development environment..."
	docker-compose up -d
	@echo "✅ Development environment started!"
	@echo "   API: http://localhost:8000"
	@echo "   Neo4j Browser: http://localhost:7474"
	@echo "   Admin Web: Run 'make web-dev' in another terminal"

docker-down:
	@echo "🛑 Stopping local development environment..."
	docker-compose down

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# =========================
# Development Tools
# =========================

seed-db:
	@echo "🌱 Seeding local databases with test data..."
	python tools/scripts/seed_databases.py

api-dev:
	@echo "🚀 Starting API in development mode..."
	cd apps/api && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web-dev:
	@echo "🌐 Starting admin web in development mode..."
	cd apps/admin_web && npm run dev

mobile-dev:
	@echo "📱 Starting mobile app in development mode..."
	cd apps/mobile && flutter run

# =========================
# Utility Commands
# =========================

install-deps:
	@echo "📦 Installing dependencies..."
	@echo "Installing Python dependencies..."
	cd apps/api && pip install -r requirements.txt -r requirements-dev.txt
	@echo "Installing Node.js dependencies..."
	cd apps/admin_web && npm install
	@echo "Installing Flutter dependencies..."
	cd apps/mobile && flutter pub get

lint:
	@echo "🔍 Running linters..."
	cd apps/api && python -m flake8 app/
	cd apps/admin_web && npm run lint
	cd apps/mobile && flutter analyze

test:
	@echo "🧪 Running tests..."
	cd apps/api && python -m pytest
	cd apps/admin_web && npm run test
	cd apps/mobile && flutter test

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	cd apps/admin_web && rm -rf node_modules dist
	cd apps/mobile && flutter clean

# =========================
# Quick Start Commands
# =========================

dev-setup: install-deps docker-build
	@echo "✅ Development environment setup complete!"
	@echo "Next steps:"
	@echo "  1. Run 'make docker-up' to start local services"
	@echo "  2. Run 'make seed-db' to populate test data"
	@echo "  3. Run 'make web-dev' to start the admin interface"

quick-start: dev-setup docker-up seed-db
	@echo "🎉 Quick start complete!"
	@echo "Your development environment is ready:"
	@echo "  • API: http://localhost:8000"
	@echo "  • Neo4j: http://localhost:7474"
	@echo "  • Run 'make web-dev' for admin interface"

# =========================
# Cost Optimization Helpers
# =========================

cost-optimize-dev:
	@echo "💰 Optimizing costs for development environment..."
	@echo "This will set min_instances=0 for all services to enable scale-to-zero"
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make cost-optimize-dev PROJECT=your-project"; exit 1; fi
	cd packages/gcp_firebase/terraform && \
	terraform workspace select dev && \
	terraform apply -var="project_id=$(PROJECT)" -var="api_min_instances=0" -var="worker_min_instances=0" -var-file=environments/dev.tfvars

scale-down-staging:
	@echo "📉 Scaling down staging environment for cost savings..."
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make scale-down-staging PROJECT=your-project"; exit 1; fi
	cd packages/gcp_firebase/terraform && \
	terraform workspace select staging && \
	terraform apply -var="project_id=$(PROJECT)" -var="api_min_instances=0" -var="worker_min_instances=0" -var-file=environments/staging.tfvars

# =========================
# Monitoring Commands
# =========================

logs-api:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make logs-api PROJECT=your-project"; exit 1; fi
	@echo "📋 Showing API logs..."
	gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name~living-twin-api" --project=$(PROJECT) --limit=50

logs-worker:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make logs-worker PROJECT=your-project"; exit 1; fi
	@echo "📋 Showing worker logs..."
	gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name~living-twin-worker" --project=$(PROJECT) --limit=50

status:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make status PROJECT=your-project"; exit 1; fi
	@echo "📊 Checking service status..."
	gcloud run services list --project=$(PROJECT) --region=europe-west1

# =========================
# Neo4j Schema Management
# =========================

init-schema:
	@echo "🔧 Initializing Neo4j schema..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required. Usage: make init-schema NEO4J_URI=bolt://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required. Usage: make init-schema NEO4J_URI=bolt://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required. Usage: make init-schema NEO4J_URI=bolt://localhost:7687 NEO4J_USER=neo4j NEO4J_PASSWORD=password"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --init

validate-schema:
	@echo "🔍 Validating Neo4j schema..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --validate

list-constraints:
	@echo "📋 Listing Neo4j constraints..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --list-constraints

list-vector-indexes:
	@echo "📋 Listing Neo4j vector indexes..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --list-vector-indexes

create-sample-data:
	@echo "🌱 Creating sample data in Neo4j..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --create-sample-data

cleanup-sample-data:
	@echo "🧹 Cleaning up sample data from Neo4j..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required"; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required"; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required"; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --cleanup-sample-data
