# =========================
# Living Twin Infrastructure - Variables
# =========================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

# Container Images
variable "api_image_url" {
  description = "Container image URL for the API service"
  type        = string
}

variable "worker_image_url" {
  description = "Container image URL for the worker service"
  type        = string
}

# Secrets (sensitive)
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "neo4j_uri" {
  description = "Neo4j database URI"
  type        = string
  sensitive   = true
}

variable "neo4j_user" {
  description = "Neo4j database user"
  type        = string
  sensitive   = true
}

variable "neo4j_password" {
  description = "Neo4j database password"
  type        = string
  sensitive   = true
}

variable "firebase_service_account_key" {
  description = "Firebase service account key (JSON)"
  type        = string
  sensitive   = true
}

# Optional overrides
variable "api_min_instances" {
  description = "Override minimum instances for API service"
  type        = number
  default     = null
}

variable "api_max_instances" {
  description = "Override maximum instances for API service"
  type        = number
  default     = null
}

variable "worker_min_instances" {
  description = "Override minimum instances for worker service"
  type        = number
  default     = null
}

variable "worker_max_instances" {
  description = "Override maximum instances for worker service"
  type        = number
  default     = null
}

variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Override backup settings"
  type        = bool
  default     = null
}

variable "notification_channels" {
  description = "Notification channels for alerts"
  type        = list(string)
  default     = []
}

# Network configuration
variable "vpc_connector_name" {
  description = "VPC connector name for private networking"
  type        = string
  default     = null
}

variable "allowed_ingress_cidrs" {
  description = "CIDR blocks allowed to access services"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Database configuration
variable "neo4j_instance_type" {
  description = "Neo4j instance type (managed or vm)"
  type        = string
  default     = "managed"
  validation {
    condition     = contains(["managed", "vm"], var.neo4j_instance_type)
    error_message = "Neo4j instance type must be either 'managed' or 'vm'."
  }
}

variable "neo4j_vm_machine_type" {
  description = "Machine type for Neo4j VM"
  type        = string
  default     = "e2-standard-4"
}

variable "neo4j_disk_size" {
  description = "Disk size for Neo4j in GB"
  type        = number
  default     = 100
}

# API Gateway configuration
variable "enable_api_gateway" {
  description = "Enable API Gateway"
  type        = bool
  default     = false
}

variable "api_gateway_config_path" {
  description = "Path to API Gateway configuration file"
  type        = string
  default     = "../api_gateway/openapi-gateway.yaml"
}

# Custom domains
variable "custom_domain" {
  description = "Custom domain for the API"
  type        = string
  default     = null
}

variable "ssl_certificate_name" {
  description = "SSL certificate name for custom domain"
  type        = string
  default     = null
}

# Feature flags
variable "enable_cloud_sql" {
  description = "Enable Cloud SQL for metadata storage"
  type        = bool
  default     = false
}

variable "enable_redis" {
  description = "Enable Redis for caching"
  type        = bool
  default     = false
}

variable "enable_bigquery" {
  description = "Enable BigQuery for analytics"
  type        = bool
  default     = false
}

# Cost optimization
variable "enable_preemptible_workers" {
  description = "Use preemptible instances for workers"
  type        = bool
  default     = false
}

variable "auto_scaling_target_cpu" {
  description = "Target CPU utilization for auto-scaling"
  type        = number
  default     = 70
}

# Security
variable "enable_binary_authorization" {
  description = "Enable Binary Authorization for container security"
  type        = bool
  default     = false
}

variable "enable_workload_identity" {
  description = "Enable Workload Identity for GKE integration"
  type        = bool
  default     = false
}

# Compliance
variable "enable_audit_logs" {
  description = "Enable audit logging"
  type        = bool
  default     = true
}

variable "data_residency_region" {
  description = "Region for data residency compliance"
  type        = string
  default     = null
}

# Development settings
variable "enable_debug_mode" {
  description = "Enable debug mode for development"
  type        = bool
  default     = false
}

variable "log_level" {
  description = "Log level for applications"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

# Integration settings
variable "notification_webhook_url" {
  description = "Webhook URL for notifications to communication platforms"
  type        = string
  default     = null
  sensitive   = true
}

variable "enable_prometheus_monitoring" {
  description = "Enable Prometheus for monitoring"
  type        = bool
  default     = false
}

variable "jira_api_token" {
  description = "Jira API token for integration"
  type        = string
  default     = null
  sensitive   = true
}

variable "jira_instance_url" {
  description = "Jira instance URL (e.g., https://your-org.atlassian.net)"
  type        = string
  default     = null
}

variable "linear_api_key" {
  description = "Linear API key for integration"
  type        = string
  default     = null
  sensitive   = true
}

variable "firecrawl_api_key" {
  description = "Firecrawl API key for web scraping"
  type        = string
  default     = null
  sensitive   = true
}

# Backup and disaster recovery
variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup"
  type        = bool
  default     = false
}

variable "disaster_recovery_region" {
  description = "Region for disaster recovery"
  type        = string
  default     = null
}

# Performance tuning
variable "api_timeout_seconds" {
  description = "API request timeout in seconds"
  type        = number
  default     = 300
}

variable "worker_timeout_seconds" {
  description = "Worker job timeout in seconds"
  type        = number
  default     = 3600
}

variable "max_concurrent_requests" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 80
}

# Environment-specific overrides
variable "environment_overrides" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    min_instances    = optional(number)
    max_instances    = optional(number)
    cpu_limit        = optional(string)
    memory_limit     = optional(string)
    enable_backup    = optional(bool)
    enable_monitoring = optional(bool)
  }))
  default = {}
}

# Tags and labels
variable "additional_labels" {
  description = "Additional labels to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = null
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = null
}
