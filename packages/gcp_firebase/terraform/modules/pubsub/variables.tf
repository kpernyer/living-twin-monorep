# =========================
# Pub/Sub Module Variables
# =========================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "topics" {
  description = "Map of Pub/Sub topics to create"
  type = map(object({
    labels                        = optional(map(string), {})
    schema_name                   = optional(string)
    schema_encoding              = optional(string, "JSON")
    push_endpoint                = optional(string)
    push_service_account         = optional(string)
    push_audience               = optional(string)
    push_attributes             = optional(map(string), {})
    iam_bindings                = optional(list(object({
      role   = string
      member = string
    })), [])
    subscription_iam_bindings   = optional(list(object({
      role   = string
      member = string
    })), [])
  }))
  default = {}
}

variable "schemas" {
  description = "Map of Pub/Sub schemas to create"
  type = map(object({
    type       = string # "AVRO" or "PROTOCOL_BUFFER"
    definition = string
  }))
  default = {}
}

variable "message_retention_duration" {
  description = "Message retention duration for topics"
  type        = string
  default     = "604800s" # 7 days
}

variable "dlq_message_retention_duration" {
  description = "Message retention duration for DLQ topics"
  type        = string
  default     = "604800s" # 7 days
}

variable "subscription_message_retention_duration" {
  description = "Message retention duration for subscriptions"
  type        = string
  default     = "604800s" # 7 days
}

variable "ack_deadline_seconds" {
  description = "Acknowledgment deadline in seconds"
  type        = number
  default     = 600 # 10 minutes
}

variable "retain_acked_messages" {
  description = "Whether to retain acknowledged messages"
  type        = bool
  default     = false
}

variable "subscription_expiration_ttl" {
  description = "TTL for subscription expiration"
  type        = string
  default     = "2678400s" # 31 days
}

variable "retry_minimum_backoff" {
  description = "Minimum backoff for retry policy"
  type        = string
  default     = "10s"
}

variable "retry_maximum_backoff" {
  description = "Maximum backoff for retry policy"
  type        = string
  default     = "600s"
}

variable "max_delivery_attempts" {
  description = "Maximum delivery attempts before sending to DLQ"
  type        = number
  default     = 5
}

variable "enable_dlq" {
  description = "Enable Dead Letter Queues"
  type        = bool
  default     = true
}

variable "create_base_subscriptions" {
  description = "Create base monitoring subscriptions"
  type        = bool
  default     = true
}

variable "create_service_account" {
  description = "Create a service account for Pub/Sub operations"
  type        = bool
  default     = true
}

variable "service_account_prefix" {
  description = "Prefix for service account name"
  type        = string
  default     = "living-twin"
}

variable "allowed_persistence_regions" {
  description = "Allowed regions for message persistence"
  type        = list(string)
  default     = null
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    managed-by = "terraform"
    project    = "living-twin"
  }
}

# Flow control settings
variable "max_outstanding_messages" {
  description = "Maximum outstanding messages for flow control"
  type        = number
  default     = 1000
}

variable "max_outstanding_bytes" {
  description = "Maximum outstanding bytes for flow control"
  type        = number
  default     = 1073741824 # 1GB
}

# Push subscription settings
variable "push_config_attributes" {
  description = "Default attributes for push subscriptions"
  type        = map(string)
  default     = {}
}

# Filtering settings
variable "enable_message_ordering" {
  description = "Enable message ordering"
  type        = bool
  default     = false
}

variable "filter_expressions" {
  description = "Map of topic names to filter expressions"
  type        = map(string)
  default     = {}
}

# Monitoring and alerting
variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "alert_notification_channels" {
  description = "Notification channels for alerts"
  type        = list(string)
  default     = []
}

# BigQuery export settings
variable "enable_bigquery_export" {
  description = "Enable BigQuery export for message analytics"
  type        = bool
  default     = false
}

variable "bigquery_dataset_id" {
  description = "BigQuery dataset ID for message export"
  type        = string
  default     = null
}

variable "bigquery_table_id" {
  description = "BigQuery table ID for message export"
  type        = string
  default     = null
}

# Cloud Storage export settings
variable "enable_cloud_storage_export" {
  description = "Enable Cloud Storage export for message archival"
  type        = bool
  default     = false
}

variable "cloud_storage_bucket" {
  description = "Cloud Storage bucket for message export"
  type        = string
  default     = null
}

variable "cloud_storage_filename_prefix" {
  description = "Filename prefix for Cloud Storage export"
  type        = string
  default     = "pubsub-messages"
}

# Encryption settings
variable "kms_key_name" {
  description = "KMS key name for message encryption"
  type        = string
  default     = null
}
