---
marp: true
theme: tech-solution
title: "Living Twin: System Management"
author: "The Living Twin Team"
date: "2025-08-16"
footer: <span class="title">Living Twin: System Management</span><span class="pagenumber"></span><span class="copyright">© 2025 Living Twin</span>
---

<!-- _class: title-page -->

![Logo](img/big-logo.jpeg)

# **Living Twin**
## System Management
<div class="date">August 16, 2025</div>

---

## Development Workflow with `uv`

The development workflow is streamlined using a `Makefile` and `uv` for a fast and efficient experience.

- **`uv` for Python**: We use `uv`, a next-generation Python package manager, to handle dependencies, virtual environments, and run scripts. This results in a significant speedup in CI/CD and local setup.
- **`make docker-up`**: Starts the local development environment using Docker Compose.
- **`make api-dev`**: Runs the FastAPI backend in development mode with hot reloading, powered by `uv`.
- **`make web-dev`**: Runs the React admin web application in development mode.
- **`make lint`**: Runs linters for Python, JavaScript, and Flutter code.
- **`make test`**: Executes the test suite for all applications.

---

## Infrastructure as Code with Terraform

The entire cloud infrastructure is managed using Terraform, ensuring a consistent and reproducible environment.

- **`terraform-plan`**: Plans infrastructure changes for a specific environment.
- **`terraform-apply`**: Applies infrastructure changes to a specific environment.
- **`terraform-destroy`**: Destroys the infrastructure for a specific environment.

The Terraform configuration is organized into modules for reusability and clarity.

---

## CI/CD Pipeline with GitHub Actions

A robust CI/CD pipeline is implemented using GitHub Actions to automate the testing and deployment process.

- **Automated Testing**: Linting, type checking, and unit tests are run on every push.
- **Multi-environment Deployment**: Automated deployment to staging and production environments.
- **Security Scanning**: Trivy is used to scan for vulnerabilities in Docker images.
- **Performance Testing**: k6 is used for load testing the application.
- **Notifications**: Deployment status is sent to the organization's communication platform.

---

## External Dependencies

The system relies on several external services and APIs:

- **Google Cloud Platform**: For hosting, database, storage, and other cloud services.
- **OpenAI API**: For natural language processing and generation.
- **Firebase**: For authentication and real-time database.
- **GitHub**: For source code management and CI/CD.
- **Communication Platforms**: For notifications.

---

## Configuration Management

A clear strategy is in place for managing environment-specific configurations.

- **Environment Variables**: Used to store sensitive information and environment-specific settings.
- **`.env` files**: Used for local development to store environment variables.
- **Google Secret Manager**: Used to store secrets for staging and production environments.
- **Configuration Files**: Separate configuration files for different environments.

---

## Monitoring with Prometheus

For advanced monitoring and alerting, the system is geared up to integrate with Prometheus.

- **Metrics Exposition**: The FastAPI backend can be configured to expose Prometheus metrics.
- **Dashboards**: Create Grafana dashboards to visualize key application and system metrics.
- **Alerting**: Set up alerting rules in Prometheus to get notified of any issues.

---

## Ticketing System Integration

The system can be integrated with ticketing systems like Jira and Linear to streamline workflows.

- **MCP Servers**: Standard MCP servers can be used to connect to Jira and Linear APIs.
- **Automated Ticket Creation**: Automatically create tickets for issues, tasks, or user feedback.
- **Two-way Sync**: Keep the system in sync with the ticketing system for real-time updates.

---

## Data Ingestion with Firecrawl and Puppeteer

To enhance the knowledge base of the system, we can use Firecrawl and Puppeteer for data ingestion.

- **Firecrawl**: An open-source tool to crawl, scrape, and convert websites into LLM-ready data.
- **Puppeteer**: A Node.js library to control a headless Chrome or Chromium browser for web scraping and automation.
- **Automated Data Ingestion**: Set up automated pipelines to ingest data from various web sources.
