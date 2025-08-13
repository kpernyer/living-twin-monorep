# =========================
# Secret Manager Module Variables
# =========================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "secrets" {
  description = "Map of secrets to create"
  type = map(object({
    secret_data           = optional(string)
    enabled              = optional(bool, true)
    labels               = optional(map(string), {})
    notification_topics  = optional(list(string), [])
    rotation_period      = optional(string)
    next_rotation_time   = optional(string)
    expire_time          = optional(string)
    ttl                  = optional(string)
    annotations          = optional(map(string), {})
    iam_bindings = optional(list(object({
      role   = string
      member = string
    })), [])
  }))
  default = {}
}

variable "replication_locations" {
  description = "List of locations for user-managed replication. If null, uses automatic replication"
  type        = list(string)
  default     = null
}

variable "kms_key_name" {
  description = "KMS key name for encryption"
  type        = string
  default     = null
}

variable "create_service_account" {
  description = "Create a service account for Secret Manager operations"
  type        = bool
  default     = true
}

variable "service_account_prefix" {
  description = "Prefix for service account name"
  type        = string
  default     = "living-twin"
}

variable "grant_admin_permissions" {
  description = "Grant admin permissions to the service account"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    managed-by = "terraform"
    project    = "living-twin"
  }
}

# Monitoring and alerting
variable "enable_monitoring" {
  description = "Enable monitoring and alerting for secrets"
  type        = bool
  default     = true
}

variable "access_alert_threshold" {
  description = "Threshold for secret access rate alerts"
  type        = number
  default     = 100
}

variable "notification_channels" {
  description = "Notification channels for alerts"
  type        = list(string)
  default     = []
}

# Backup configuration
variable "enable_backup" {
  description = "Enable backup of secrets to Cloud Storage"
  type        = bool
  default     = false
}

variable "backup_location" {
  description = "Location for backup bucket"
  type        = string
  default     = "US"
}

variable "backup_retention_days" {
  description = "Retention period for backups in days"
  type        = number
  default     = 90
}

variable "backup_kms_key_name" {
  description = "KMS key name for backup encryption"
  type        = string
  default     = null
}

# Secret rotation configuration
variable "enable_automatic_rotation" {
  description = "Enable automatic rotation for secrets"
  type        = bool
  default     = false
}

variable "default_rotation_period" {
  description = "Default rotation period for secrets"
  type        = string
  default     = "2592000s" # 30 days
}

# Access control
variable "default_accessor_members" {
  description = "Default members to grant secret accessor role"
  type        = list(string)
  default     = []
}

variable "default_admin_members" {
  description = "Default members to grant secret admin role"
  type        = list(string)
  default     = []
}

# Audit and compliance
variable "enable_audit_logging" {
  description = "Enable audit logging for secret access"
  type        = bool
  default     = true
}

variable "audit_log_retention_days" {
  description = "Retention period for audit logs in days"
  type        = number
  default     = 365
}

# Integration settings
variable "pubsub_topic_for_notifications" {
  description = "Pub/Sub topic for secret change notifications"
  type        = string
  default     = null
}

variable "cloud_function_trigger" {
  description = "Cloud Function to trigger on secret changes"
  type        = string
  default     = null
}

# Environment-specific settings
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "secret_name_prefix" {
  description = "Prefix for secret names"
  type        = string
  default     = ""
}

variable "secret_name_suffix" {
  description = "Suffix for secret names"
  type        = string
  default     = ""
}

# Security settings
variable "require_encryption" {
  description = "Require encryption for all secrets"
  type        = bool
  default     = true
}

variable "allowed_accessor_domains" {
  description = "List of domains allowed to access secrets"
  type        = list(string)
  default     = []
}

variable "enable_vpc_sc" {
  description = "Enable VPC Service Controls for Secret Manager"
  type        = bool
  default     = false
}

# Performance and scaling
variable "max_versions_per_secret" {
  description = "Maximum number of versions to keep per secret"
  type        = number
  default     = 10
}

variable "enable_regional_secrets" {
  description = "Enable regional secrets for better performance"
  type        = bool
  default     = false
}

# Cost optimization
variable "enable_lifecycle_management" {
  description = "Enable lifecycle management for secrets"
  type        = bool
  default     = true
}

variable "unused_secret_ttl" {
  description = "TTL for unused secrets"
  type        = string
  default     = "7776000s" # 90 days
}
