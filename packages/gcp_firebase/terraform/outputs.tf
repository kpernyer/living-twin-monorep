# =========================
# Living Twin Infrastructure - Outputs
# =========================

# Environment information
output "environment" {
  description = "Current environment (workspace)"
  value       = local.environment
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

# =========================
# Cloud Run Services
# =========================
output "api_service_url" {
  description = "URL of the API service"
  value       = module.cloud_run_api.service_url
}

output "api_service_name" {
  description = "Name of the API service"
  value       = module.cloud_run_api.service_name
}

output "api_service_account_email" {
  description = "Service account email for API service"
  value       = module.cloud_run_api.service_account_email
}

output "worker_service_url" {
  description = "URL of the worker service"
  value       = module.cloud_run_worker.service_url
}

output "worker_service_name" {
  description = "Name of the worker service"
  value       = module.cloud_run_worker.service_name
}

output "worker_service_account_email" {
  description = "Service account email for worker service"
  value       = module.cloud_run_worker.service_account_email
}

# =========================
# Pub/Sub Configuration
# =========================
output "pubsub_topics" {
  description = "Created Pub/Sub topics"
  value       = module.pubsub.topic_names
}

output "pubsub_dlq_topics" {
  description = "Created Pub/Sub DLQ topics"
  value       = module.pubsub.dlq_topic_names
}

output "pubsub_subscriptions" {
  description = "Created Pub/Sub subscriptions"
  value       = module.pubsub.subscription_names
}

output "pubsub_service_account_email" {
  description = "Pub/Sub service account email"
  value       = module.pubsub.service_account_email
}

# =========================
# Secret Manager Configuration
# =========================
output "secret_names" {
  description = "Created secrets"
  value       = module.secret_manager.secret_names
  sensitive   = true
}

output "secret_manager_service_account_email" {
  description = "Secret Manager service account email"
  value       = module.secret_manager.service_account_email
}

# =========================
# Storage Configuration
# =========================
output "document_storage_bucket" {
  description = "Document storage bucket name"
  value       = google_storage_bucket.document_storage.name
}

output "document_storage_url" {
  description = "Document storage bucket URL"
  value       = google_storage_bucket.document_storage.url
}

output "backup_storage_bucket" {
  description = "Backup storage bucket name"
  value       = local.current_env.enable_backup ? google_storage_bucket.backup_storage[0].name : null
}

output "backup_storage_url" {
  description = "Backup storage bucket URL"
  value       = local.current_env.enable_backup ? google_storage_bucket.backup_storage[0].url : null
}

# =========================
# CI/CD Integration Outputs
# =========================
output "ci_cd_config" {
  description = "Configuration for CI/CD pipelines"
  value = {
    project_id    = var.project_id
    region        = var.region
    environment   = local.environment
    
    # Service information
    api_service_name    = module.cloud_run_api.service_name
    worker_service_name = module.cloud_run_worker.service_name
    
    # Container registry
    registry_url = "${var.region}-docker.pkg.dev/${var.project_id}/living-twin-repo"
    
    # Service accounts
    api_service_account    = module.cloud_run_api.service_account_email
    worker_service_account = module.cloud_run_worker.service_account_email
    
    # Pub/Sub topics for CI/CD notifications
    topics = module.pubsub.topic_publish_urls
    
    # Secret references
    secret_references = module.secret_manager.secret_references
  }
  sensitive = true
}

# =========================
# Application Configuration
# =========================
output "app_config" {
  description = "Application configuration"
  value = {
    environment = local.environment
    project_id  = var.project_id
    region      = var.region
    
    # Service URLs
    api_url    = module.cloud_run_api.service_url
    worker_url = module.cloud_run_worker.service_url
    
    # Storage
    document_bucket = google_storage_bucket.document_storage.name
    backup_bucket   = local.current_env.enable_backup ? google_storage_bucket.backup_storage[0].name : null
    
    # Pub/Sub
    pubsub_topics       = module.pubsub.topic_names
    pubsub_subscriptions = module.pubsub.subscription_names
    
    # Monitoring
    monitoring_enabled = var.enable_monitoring
  }
}

# =========================
# Monitoring and Alerting
# =========================
output "monitoring_config" {
  description = "Monitoring configuration"
  value = var.enable_monitoring ? {
    secret_manager_monitoring = module.secret_manager.monitoring_config
    notification_channels     = var.notification_channels
  } : null
}

# =========================
# Security Configuration
# =========================
output "security_config" {
  description = "Security configuration"
  value = {
    # Service accounts
    service_accounts = {
      api            = module.cloud_run_api.service_account_email
      worker         = module.cloud_run_worker.service_account_email
      pubsub         = module.pubsub.service_account_email
      secret_manager = module.secret_manager.service_account_email
    }
    
    # IAM bindings
    pubsub_iam_bindings = module.pubsub.topic_iam_bindings
    secret_iam_bindings = module.secret_manager.secret_iam_bindings
    
    # Security features
    audit_logs_enabled = var.enable_audit_logs
  }
  sensitive = true
}

# =========================
# Cost Tracking
# =========================
output "cost_tracking" {
  description = "Cost tracking information"
  value = {
    environment   = local.environment
    cost_center   = var.cost_center
    owner         = var.owner
    
    # Resource counts
    cloud_run_services = 2
    pubsub_topics     = length(module.pubsub.topic_names)
    secrets           = module.secret_manager.secret_count
    storage_buckets   = local.current_env.enable_backup ? 2 : 1
    
    # Labels for cost allocation
    common_labels = local.common_labels
  }
}

# =========================
# Terraform State Information
# =========================
output "terraform_state" {
  description = "Terraform state information"
  value = {
    workspace = terraform.workspace
    backend   = "gcs"
    bucket    = "living-twin-terraform-state"
    prefix    = "terraform/state"
  }
}

# =========================
# Environment-Specific Outputs
# =========================
output "environment_config" {
  description = "Environment-specific configuration"
  value = {
    environment = local.environment
    config      = local.current_env
    
    # Service scaling
    api_scaling = {
      min_instances = local.current_env.min_instances
      max_instances = local.current_env.max_instances
      cpu_limit     = local.current_env.cpu_limit
      memory_limit  = local.current_env.memory_limit
    }
    
    # Feature flags
    features = {
      dlq_enabled    = local.current_env.enable_dlq
      backup_enabled = local.current_env.enable_backup
    }
  }
}

# =========================
# Integration Endpoints
# =========================
output "integration_endpoints" {
  description = "Endpoints for external integrations"
  value = {
    # API endpoints
    api_base_url = module.cloud_run_api.service_url
    health_check = "${module.cloud_run_api.service_url}/healthz"
    metrics      = "${module.cloud_run_api.service_url}/metrics"
    
    # Worker endpoints
    worker_health = "${module.cloud_run_worker.service_url}/health"
    
    # Pub/Sub endpoints
    pubsub_publish_urls = module.pubsub.topic_publish_urls
    
    # Storage endpoints
    document_storage_url = google_storage_bucket.document_storage.url
  }
}

# =========================
# Deployment Information
# =========================
output "deployment_info" {
  description = "Deployment information for documentation"
  value = {
    deployed_at = timestamp()
    environment = local.environment
    terraform_version = "~> 1.5"
    
    # Service versions (would be populated by CI/CD)
    services = {
      api = {
        name = module.cloud_run_api.service_name
        url  = module.cloud_run_api.service_url
      }
      worker = {
        name = module.cloud_run_worker.service_name
        url  = module.cloud_run_worker.service_url
      }
    }
    
    # Infrastructure components
    components = {
      pubsub_topics    = length(module.pubsub.topic_names)
      secrets          = module.secret_manager.secret_count
      storage_buckets  = local.current_env.enable_backup ? 2 : 1
      firestore_indexes = 2
    }
  }
}

# =========================
# Debug Information (for development)
# =========================
output "debug_info" {
  description = "Debug information (only in dev environment)"
  value = local.environment == "dev" ? {
    local_environment = local.environment
    current_env_config = local.current_env
    pubsub_topics_config = local.pubsub_topics
    secrets_config_keys = keys(local.secrets_config)
    common_labels = local.common_labels
  } : null
  sensitive = true
}
