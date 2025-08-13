# =========================
# Secret Manager Module
# =========================

# Secrets
resource "google_secret_manager_secret" "secrets" {
  for_each = var.secrets
  
  secret_id = each.key
  project   = var.project_id
  
  replication {
    dynamic "user_managed" {
      for_each = var.replication_locations != null ? [1] : []
      content {
        dynamic "replicas" {
          for_each = var.replication_locations
          content {
            location = replicas.value
            dynamic "customer_managed_encryption" {
              for_each = var.kms_key_name != null ? [1] : []
              content {
                kms_key_name = var.kms_key_name
              }
            }
          }
        }
      }
    }
    
    dynamic "automatic" {
      for_each = var.replication_locations == null ? [1] : []
      content {
        dynamic "customer_managed_encryption" {
          for_each = var.kms_key_name != null ? [1] : []
          content {
            kms_key_name = var.kms_key_name
          }
        }
      }
    }
  }
  
  labels = merge(var.labels, each.value.labels)
  
  dynamic "topics" {
    for_each = each.value.notification_topics
    content {
      name = topics.value
    }
  }
  
  dynamic "rotation" {
    for_each = each.value.rotation_period != null ? [1] : []
    content {
      rotation_period = each.value.rotation_period
      next_rotation_time = each.value.next_rotation_time
    }
  }
  
  expire_time = each.value.expire_time
  ttl         = each.value.ttl
  
  annotations = each.value.annotations
}

# Secret versions
resource "google_secret_manager_secret_version" "secret_versions" {
  for_each = {
    for k, v in var.secrets : k => v
    if v.secret_data != null
  }
  
  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value.secret_data
  enabled     = each.value.enabled
  
  depends_on = [google_secret_manager_secret.secrets]
}

# IAM bindings for secrets
resource "google_secret_manager_secret_iam_member" "secret_accessors" {
  for_each = {
    for binding in local.secret_iam_bindings : "${binding.secret}-${binding.member}-${binding.role}" => binding
  }
  
  project   = var.project_id
  secret_id = each.value.secret
  role      = each.value.role
  member    = each.value.member
  
  depends_on = [google_secret_manager_secret.secrets]
}

# Service account for Secret Manager operations
resource "google_service_account" "secret_manager_sa" {
  count = var.create_service_account ? 1 : 0
  
  account_id   = "${var.service_account_prefix}-secret-sa"
  display_name = "Secret Manager Service Account"
  project      = var.project_id
}

# IAM bindings for the service account
resource "google_project_iam_member" "secret_manager_accessor" {
  count = var.create_service_account ? 1 : 0
  
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.secret_manager_sa[0].email}"
}

resource "google_project_iam_member" "secret_manager_viewer" {
  count = var.create_service_account ? 1 : 0
  
  project = var.project_id
  role    = "roles/secretmanager.viewer"
  member  = "serviceAccount:${google_service_account.secret_manager_sa[0].email}"
}

# Optional: Secret Manager admin role for the service account
resource "google_project_iam_member" "secret_manager_admin" {
  count = var.create_service_account && var.grant_admin_permissions ? 1 : 0
  
  project = var.project_id
  role    = "roles/secretmanager.admin"
  member  = "serviceAccount:${google_service_account.secret_manager_sa[0].email}"
}

# Local values for IAM bindings
locals {
  secret_iam_bindings = flatten([
    for secret_name, secret_config in var.secrets : [
      for binding in secret_config.iam_bindings : {
        secret = secret_name
        role   = binding.role
        member = binding.member
      }
    ]
  ])
}

# Monitoring and alerting for secrets
resource "google_monitoring_alert_policy" "secret_access_alerts" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "Secret Manager Access Alerts"
  project      = var.project_id
  
  conditions {
    display_name = "Secret access rate"
    
    condition_threshold {
      filter          = "resource.type=\"secretmanager.googleapis.com/Secret\""
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = var.access_alert_threshold
      duration        = "300s"
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
  
  enabled = true
}

# Log-based metrics for secret access
resource "google_logging_metric" "secret_access_metric" {
  count = var.enable_monitoring ? 1 : 0
  
  name    = "secret_manager_access_count"
  project = var.project_id
  
  filter = <<-EOT
    resource.type="secretmanager.googleapis.com/Secret"
    protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AccessSecretVersion"
  EOT
  
  metric_descriptor {
    metric_kind = "COUNTER"
    value_type  = "INT64"
    display_name = "Secret Manager Access Count"
  }
  
  label_extractors = {
    secret_name = "EXTRACT(resource.labels.secret_id)"
    user        = "EXTRACT(protoPayload.authenticationInfo.principalEmail)"
  }
}

# Backup configuration for secrets
resource "google_storage_bucket" "secret_backup" {
  count = var.enable_backup ? 1 : 0
  
  name     = "${var.project_id}-secret-manager-backup"
  location = var.backup_location
  project  = var.project_id
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }
  
  encryption {
    default_kms_key_name = var.backup_kms_key_name
  }
  
  labels = merge(var.labels, {
    purpose = "secret-backup"
  })
}

# IAM for backup bucket
resource "google_storage_bucket_iam_member" "backup_bucket_admin" {
  count = var.enable_backup && var.create_service_account ? 1 : 0
  
  bucket = google_storage_bucket.secret_backup[0].name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.secret_manager_sa[0].email}"
}
