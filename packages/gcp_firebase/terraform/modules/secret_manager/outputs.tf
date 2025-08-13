# =========================
# Secret Manager Module Outputs
# =========================

output "secret_names" {
  description = "Names of created secrets"
  value       = { for k, v in google_secret_manager_secret.secrets : k => v.name }
}

output "secret_ids" {
  description = "IDs of created secrets"
  value       = { for k, v in google_secret_manager_secret.secrets : k => v.id }
}

output "secret_version_names" {
  description = "Names of created secret versions"
  value       = { for k, v in google_secret_manager_secret_version.secret_versions : k => v.name }
}

output "secret_version_ids" {
  description = "IDs of created secret versions"
  value       = { for k, v in google_secret_manager_secret_version.secret_versions : k => v.id }
}

output "service_account_email" {
  description = "Email of the Secret Manager service account"
  value       = var.create_service_account ? google_service_account.secret_manager_sa[0].email : null
}

output "service_account_id" {
  description = "ID of the Secret Manager service account"
  value       = var.create_service_account ? google_service_account.secret_manager_sa[0].id : null
}

output "service_account_name" {
  description = "Name of the Secret Manager service account"
  value       = var.create_service_account ? google_service_account.secret_manager_sa[0].name : null
}

output "backup_bucket_name" {
  description = "Name of the backup bucket"
  value       = var.enable_backup ? google_storage_bucket.secret_backup[0].name : null
}

output "backup_bucket_url" {
  description = "URL of the backup bucket"
  value       = var.enable_backup ? google_storage_bucket.secret_backup[0].url : null
}

# Outputs for CI/CD integration
output "secret_access_urls" {
  description = "URLs for accessing secrets (for CI/CD)"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => "projects/${var.project_id}/secrets/${v.secret_id}/versions/latest"
  }
}

output "secret_resource_names" {
  description = "Full resource names for secrets"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => "projects/${var.project_id}/secrets/${v.secret_id}"
  }
}

# Outputs for application configuration
output "secret_config" {
  description = "Secret configuration for application use"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => {
      name       = v.name
      secret_id  = v.secret_id
      project    = var.project_id
      labels     = v.labels
      has_data   = contains(keys(google_secret_manager_secret_version.secret_versions), k)
    }
  }
}

# Outputs for monitoring and alerting
output "monitoring_config" {
  description = "Monitoring configuration"
  value = var.enable_monitoring ? {
    alert_policy_name = google_monitoring_alert_policy.secret_access_alerts[0].name
    metric_name       = google_logging_metric.secret_access_metric[0].name
    threshold         = var.access_alert_threshold
  } : null
}

# Outputs for IAM and security
output "secret_iam_bindings" {
  description = "Secret IAM bindings applied"
  value = {
    for binding in local.secret_iam_bindings : "${binding.secret}-${binding.role}" => {
      secret = binding.secret
      role   = binding.role
      member = binding.member
    }
  }
}

output "accessor_service_accounts" {
  description = "Service accounts with secret accessor permissions"
  value = var.create_service_account ? [google_service_account.secret_manager_sa[0].email] : []
}

# Outputs for environment-specific configuration
output "environment_config" {
  description = "Environment-specific Secret Manager configuration"
  value = {
    project_id                = var.project_id
    environment              = var.environment
    secrets                  = { for k, v in google_secret_manager_secret.secrets : k => v.secret_id }
    service_account_email    = var.create_service_account ? google_service_account.secret_manager_sa[0].email : null
    backup_enabled          = var.enable_backup
    backup_bucket           = var.enable_backup ? google_storage_bucket.secret_backup[0].name : null
    monitoring_enabled      = var.enable_monitoring
    kms_key_name           = var.kms_key_name
    replication_locations  = var.replication_locations
  }
}

# Outputs for Terraform state management
output "all_secret_names" {
  description = "All secret names"
  value = [for v in google_secret_manager_secret.secrets : v.name]
}

output "secrets_with_versions" {
  description = "Secrets that have versions created"
  value = [for k, v in google_secret_manager_secret_version.secret_versions : k]
}

# Outputs for integration with other modules
output "secret_references" {
  description = "Secret references for use in other modules"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => {
      secret_name = v.secret_id
      version     = "latest"
    }
  }
}

# Outputs for Cloud Run integration
output "cloud_run_secret_env_vars" {
  description = "Secret environment variables for Cloud Run"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => {
      secret_name = v.secret_id
      version     = "latest"
    }
  }
}

# Outputs for debugging and troubleshooting
output "secret_creation_time" {
  description = "Creation time of secrets"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => v.create_time
  }
}

output "secret_labels" {
  description = "Labels applied to secrets"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => v.labels
  }
}

# Outputs for cost tracking
output "secret_count" {
  description = "Total number of secrets created"
  value = length(google_secret_manager_secret.secrets)
}

output "secret_version_count" {
  description = "Total number of secret versions created"
  value = length(google_secret_manager_secret_version.secret_versions)
}

# Outputs for compliance and audit
output "audit_config" {
  description = "Audit configuration"
  value = {
    audit_logging_enabled    = var.enable_audit_logging
    audit_log_retention_days = var.audit_log_retention_days
    monitoring_enabled       = var.enable_monitoring
    backup_enabled          = var.enable_backup
    encryption_enabled      = var.kms_key_name != null
  }
}

# Outputs for rotation management
output "rotation_config" {
  description = "Rotation configuration for secrets"
  value = {
    for k, v in var.secrets : k => {
      rotation_enabled = v.rotation_period != null
      rotation_period  = v.rotation_period
      next_rotation    = v.next_rotation_time
    } if v.rotation_period != null
  }
}
