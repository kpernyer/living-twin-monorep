# =========================
# Living Twin Monorepo - Makefile
# =========================
# 
# Note: Simulation engine has been moved to separate repository:
# https://github.com/living-twin/living-twin-simulation
#
# This Makefile covers the main Living Twin platform components:
# - API (FastAPI with strategic intelligence)
# - Admin Web (React/TypeScript)
# - Mobile App (Flutter)
# - Infrastructure (Terraform/GCP)
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
	@echo "  fix-deps                                    Fix Python dependency conflicts"
	@echo "  fix-npm-vulnerabilities                     Fix npm security vulnerabilities"
	@echo "  fix-npm-vulnerabilities-force               Force fix npm vulnerabilities (breaking changes)"
	@echo "  check-node-version                          Check Node.js and npm versions"
	@echo "  install-flutter                             Install Flutter SDK"
	@echo "  check-flutter                               Check Flutter installation"
	@echo "  seed-db                                     Seed local databases with test data"
	@echo "  api-dev                                     Run API in development mode"
	@echo "  web-dev                                     Run admin web in development mode"
	@echo "  mobile-dev                                  Run mobile app in development mode"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  lint                                        Run all linters (Python, JS, Flutter)"
	@echo "  lint-strict                                 Run linters with type checking"
	@echo "  lint-python                                 Run Python linters only"
	@echo "  lint-js                                     Run JavaScript/TypeScript linters only"
	@echo "  lint-flutter                                Run Flutter linters only"
	@echo "  format                                      Auto-format all code"
	@echo ""
	@echo "📝 Examples:"
	@echo "  make check-costs ENV=dev PROJECT=my-living-twin-project"
	@echo "  make terraform-plan ENV=staging PROJECT=my-living-twin-project"
	@echo "  make docker-up"
	@echo ""
	@echo "🧪 For Simulation Engine:"
	@echo "  See: https://github.com/living-twin/living-twin-simulation"

# =========================
# Cost & Resource Management
# =========================

check-costs:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make check-costs ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make check-costs ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "🔍 Checking costs and resource utilization for $(ENV) environment..."
	python3 tools/scripts/check_resource_utilization.py --project-id $(PROJECT) --environment $(ENV)

check-resources:
	@if [ -z "$(PROJECT)" ]; then echo "❌ PROJECT is required. Usage: make check-resources ENV=dev PROJECT=your-project"; exit 1; fi
	@if [ -z "$(ENV)" ]; then echo "❌ ENV is required. Usage: make check-resources ENV=dev PROJECT=your-project"; exit 1; fi
	@echo "⚙️  Showing scaling configuration for $(ENV) environment..."
	python3 tools/scripts/check_resource_utilization.py --project-id $(PROJECT) --environment $(ENV) --show-config

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
	docker-compose down -v
	docker-compose up -d
	@echo "✅ Development environment started!"
	@echo "   API: http://localhost:8000"
	@echo "   Neo4j Browser: http://localhost:7474"
	@echo "   Admin Web: http://localhost:5173"
	@echo "   Firebase Emulator UI: http://localhost:4000"
	@echo "   Firestore Emulator: http://localhost:8080 | Auth Emulator: http://localhost:9099"
	@echo "   Tip: Run 'make seed-db' to populate sample data"

docker-down:
	@echo "🛑 Stopping local development environment..."
	docker-compose down -v

docker-stop:
	@echo "🛑 Stopping local development containers..."
	docker-compose stop

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# =========================
# Development Tools
# =========================

seed-db:
	@echo "🌱 Seeding local databases with test data..."
	python3 tools/scripts/seed_databases.py

api-dev:
	@echo "🚀 Starting API in development mode with uv..."
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web-dev:
	@echo "🌐 Starting admin web in development mode..."
	pnpm dev

mobile-dev:
	@echo "📱 Starting mobile app in development mode..."
	cd apps/mobile && flutter run

# =========================
# Utility Commands
# =========================

install-deps:
	@echo "📦 Installing dependencies with uv and pnpm..."
	@if ! command -v uv &> /dev/null; then \
		echo "⚠️  uv not found. Installing uv..."; \
		pip install uv; \
	fi
	@if ! command -v pnpm &> /dev/null; then \
		echo "⚠️  pnpm not found. Installing pnpm..."; \
		npm install -g pnpm; \
	fi
	@echo "Installing Python dependencies..."
	cd apps/api && uv pip install --system --no-cache --compile -e .[dev]
	@echo "Installing Node.js dependencies..."
	pnpm install
	@echo "Auditing Node.js dependencies for vulnerabilities..."
	pnpm audit --audit-level moderate || echo "⚠️  Found vulnerabilities. Run 'make fix-npm-vulnerabilities' to fix them."
	@echo "Checking Flutter installation..."
	@if ! command -v flutter &> /dev/null && ! [ -f /opt/flutter/bin/flutter ]; then \
		echo "⚠️  Flutter not found. Installing Flutter..."; \
		$(MAKE) install-flutter; \
	fi
	@echo "Installing Flutter dependencies..."
	@if command -v flutter &> /dev/null; then \
		echo "Using Flutter from PATH"; \
		cd apps/mobile && flutter pub get; \
	elif [ -f /opt/flutter/bin/flutter ]; then \
		echo "Using Flutter from /opt/flutter/bin/flutter"; \
		cd apps/mobile && /opt/flutter/bin/flutter pub get; \
	else \
		echo "❌ Flutter not found in PATH or /opt/flutter/bin/flutter"; \
		echo "⚠️  Please restart your terminal and run: source ~/.bashrc"; \
		echo "⚠️  Then run: make install-deps again"; \
		exit 1; \
	fi

fix-deps:
	@echo "🔧 Fixing dependency conflicts..."
	python3 tools/scripts/fix_dependencies.py

fix-npm-vulnerabilities:
	@echo "🔒 Fixing npm security vulnerabilities..."
	pnpm audit --fix
	@echo "Checking for remaining vulnerabilities..."
	pnpm audit --audit-level moderate || echo "⚠️  Some vulnerabilities may require manual review"

fix-npm-vulnerabilities-force:
	@echo "🔒 Force fixing npm security vulnerabilities (may include breaking changes)..."
	@echo "⚠️  This may introduce breaking changes!"
	@read -p "Continue with force fix? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	pnpm audit --fix --force
	@echo "Checking for remaining vulnerabilities..."
	pnpm audit --audit-level moderate || echo "⚠️  Some vulnerabilities may require manual review"

check-node-version:
	@echo "📋 Checking Node.js and npm versions..."
	@echo "Current Node.js version:"
	node --version
	@echo "Current npm version:"
	npm --version
	@echo "Recommended Node.js version (from .nvmrc):"
	@if [ -f .nvmrc ]; then cat .nvmrc; else echo "No .nvmrc file found"; fi
	@echo "Latest npm version available:"
	npm view npm version

install-flutter:
	@echo "📱 Installing Flutter..."
	@if command -v flutter &> /dev/null; then \
		echo "✅ Flutter is already installed:"; \
		flutter --version; \
		echo "🔧 Configuring Flutter..."; \
		flutter config --no-cli-animations; \
		flutter config --no-analytics; \
		echo "🔄 Checking for Flutter updates..."; \
		flutter upgrade || echo "⚠️  Flutter upgrade failed, continuing with current version"; \
		exit 0; \
	fi
	@echo "🔍 Detecting operating system..."
	@if [ "$$(uname)" = "Linux" ]; then \
		echo "🐧 Installing Flutter on Linux..."; \
		cd /tmp && \
		echo "📥 Downloading Flutter SDK..."; \
		wget -q https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.27.1-stable.tar.xz -O flutter.tar.xz && \
		echo "📦 Extracting Flutter..."; \
		tar xf flutter.tar.xz && \
		echo "📁 Moving Flutter to /opt/flutter..."; \
		sudo mv flutter /opt/flutter && \
		echo "🔗 Adding Flutter to PATH..."; \
		echo 'export PATH="/opt/flutter/bin:$$PATH"' >> ~/.bashrc && \
		echo 'export PATH="/opt/flutter/bin:$$PATH"' >> ~/.zshrc 2>/dev/null || true && \
		export PATH="/opt/flutter/bin:$$PATH" && \
		echo "🔧 Configuring Flutter..."; \
		/opt/flutter/bin/flutter config --no-cli-animations && \
		/opt/flutter/bin/flutter config --no-analytics && \
		echo "🔧 Running Flutter doctor..."; \
		/opt/flutter/bin/flutter doctor && \
		echo "✅ Flutter installed successfully!"; \
		echo "⚠️  Flutter is available at /opt/flutter/bin/flutter"; \
		echo "⚠️  Please restart your terminal or run: source ~/.bashrc"; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		echo "🍎 Installing Flutter on macOS..."; \
		if command -v brew &> /dev/null; then \
			brew install --cask flutter && \
			echo "🔧 Configuring Flutter..."; \
			flutter config --no-cli-animations && \
			flutter config --no-analytics && \
			echo "✅ Flutter installed via Homebrew!"; \
		else \
			echo "❌ Homebrew not found. Please install Homebrew first or install Flutter manually."; \
			echo "Visit: https://flutter.dev/docs/get-started/install/macos"; \
			exit 1; \
		fi; \
	else \
		echo "❌ Unsupported operating system: $$(uname)"; \
		echo "Please install Flutter manually: https://flutter.dev/docs/get-started/install"; \
		exit 1; \
	fi

check-flutter:
	@echo "📱 Checking Flutter installation..."
	@if command -v flutter &> /dev/null; then \
		echo "✅ Flutter is installed:"; \
		flutter --version; \
		echo "🔍 Running Flutter doctor..."; \
		flutter doctor; \
	else \
		echo "❌ Flutter is not installed."; \
		echo "Run 'make install-flutter' to install Flutter."; \
		exit 1; \
	fi

lint:
	@echo "🔍 Running linters..."
	cd apps/api && python3 -m flake8 app/ --max-line-length=100 --ignore=E203,W503 || echo "⚠️  flake8 issues found"
	cd apps/api && python3 -m black --check app/ --line-length=100 || echo "⚠️  black formatting issues found"
	cd apps/api && python3 -m isort --check-only app/ --profile=black --line-length=100 || echo "⚠️  isort import issues found"
	cd apps/admin_web && npm run lint || echo "⚠️  npm lint issues found"
	@if command -v flutter &> /dev/null; then \
		cd apps/mobile && flutter analyze || echo "⚠️  Flutter analysis issues found"; \
	elif [ -f /opt/flutter/bin/flutter ]; then \
		cd apps/mobile && /opt/flutter/bin/flutter analyze || echo "⚠️  Flutter analysis issues found"; \
	else \
		echo "⚠️  Flutter not found, skipping Flutter analysis"; \
	fi

lint-strict:
	@echo "🔍 Running strict linters with type checking..."
	cd apps/api && python3 -m flake8 app/ --max-line-length=100 --ignore=E203,W503
	cd apps/api && python3 -m black --check app/ --line-length=100
	cd apps/api && python3 -m isort --check-only app/ --profile=black --line-length=100
	cd apps/api && python3 -m mypy app/
	cd apps/admin_web && npm run lint
	@if command -v flutter &> /dev/null; then \
		cd apps/mobile && flutter analyze; \
	elif [ -f /opt/flutter/bin/flutter ]; then \
		cd apps/mobile && /opt/flutter/bin/flutter analyze; \
	else \
		echo "⚠️  Flutter not found, skipping Flutter analysis"; \
	fi

lint-python:
	@echo "🐍 Running Python linters..."
	cd apps/api && python3 -m flake8 app/ --max-line-length=100 --ignore=E203,W503
	cd apps/api && python3 -m black --check app/ --line-length=100
	cd apps/api && python3 -m isort --check-only app/ --profile=black --line-length=100
	cd apps/api && python3 -m mypy app/

lint-js:
	@echo "🌐 Running JavaScript/TypeScript linters..."
	pnpm lint
	@echo "🌐 Running markdown linter..."
	pnpm exec markdownlint "**/*.md" --ignore-path .markdownlintignore --config .markdownlint.json

lint-flutter:
	@echo "📱 Running Flutter linters..."
	@if command -v flutter &> /dev/null; then \
		cd apps/mobile && flutter analyze; \
	elif [ -f /opt/flutter/bin/flutter ]; then \
		cd apps/mobile && /opt/flutter/bin/flutter analyze; \
	else \
		echo "❌ Flutter not found. Run 'make install-flutter' first."; \
		exit 1; \
	fi

test:
	@echo "🧪 Running tests..."
	cd apps/api && python -m pytest tests/ -v
	pnpm test
	cd apps/mobile && flutter test

test-unit:
	@echo "🧪 Running unit tests only..."
	cd apps/api && python -m pytest tests/ -v -m "not integration"
	cd apps/admin_web && npm run test
	cd apps/mobile && flutter test

test-integration:
	@echo "🧪 Running integration tests..."
	cd apps/api && python -m pytest tests/test_integration.py -v -m integration

format:
	@echo "🎨 Formatting code..."
	cd apps/api && python -m black app/ --line-length=100
	cd apps/api && python -m isort app/ --profile=black --line-length=100
	pnpm format
	cd apps/mobile && dart format lib/

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

ensure-vector-index:
	@echo "🧭 Ensuring Neo4j vector index matches embedding dimensions..."
	@if [ -z "$(NEO4J_URI)" ]; then echo "❌ NEO4J_URI is required."; exit 1; fi
	@if [ -z "$(NEO4J_USER)" ]; then echo "❌ NEO4J_USER is required."; exit 1; fi
	@if [ -z "$(NEO4J_PASSWORD)" ]; then echo "❌ NEO4J_PASSWORD is required."; exit 1; fi
	@if [ -z "$(VECTOR_DIM)" ]; then echo "❌ VECTOR_DIM is required (e.g., 1536 for OpenAI, 384 for SBERT)."; exit 1; fi
	python tools/scripts/manage_neo4j_schema.py --uri $(NEO4J_URI) --user $(NEO4J_USER) --password $(NEO4J_PASSWORD) --ensure-vector-index --vi-name docEmbeddings --vi-label Doc --vi-property embedding --vi-dim $(VECTOR_DIM) --vi-sim cosine

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

# =========================
# Presentations
# =========================

# Find all markdown files in the presentations directory
PRESENTATIONS_MD := $(wildcard presentations/*.md)

# Create corresponding html and pptx file names
PRESENTATIONS_HTML := $(patsubst presentations/%.md,presentations/export/html/%.html,$(PRESENTATIONS_MD))
PRESENTATIONS_PPTX := $(patsubst presentations/%.md,presentations/export/ppt/%.pptx,$(PRESENTATIONS_MD))

# The main target depends on all the final output files
build-presentations: $(PRESENTATIONS_HTML) $(PRESENTATIONS_PPTX)
	@echo "✅ All presentations are up to date."

# Rule to build HTML files from Markdown files
presentations/export/html/%.html: presentations/%.md presentations/css/theme.css presentations/img/*
	@echo "Building HTML presentation for $<..."
	@mkdir -p presentations/export/html
	marp --html --allow-local-files --theme presentations/css/theme.css $< -o $@

# Rule to build PowerPoint files from Markdown files
presentations/export/ppt/%.pptx: presentations/%.md presentations/css/theme.css presentations/img/*
	@echo "Building PowerPoint presentation for $<..."
	@mkdir -p presentations/export/ppt
	marp --pptx --allow-local-files --theme presentations/css/theme.css $< -o $@

clean-presentations:
	@echo "🧹 Cleaning up presentations..."
	rm -rf presentations/export
