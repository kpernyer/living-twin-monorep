# =========================
# Cloud Run Module Variables
# =========================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "image_url" {
  description = "Container image URL"
  type        = string
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "cpu_limit" {
  description = "CPU limit"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit"
  type        = string
  default     = "2Gi"
}

variable "cpu_idle" {
  description = "CPU allocation during idle"
  type        = bool
  default     = true
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "request_timeout" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "ingress_type" {
  description = "Ingress type for the service"
  type        = string
  default     = "INGRESS_ALL"
  validation {
    condition = contains([
      "INGRESS_ALL",
      "INGRESS_INTERNAL",
      "INGRESS_INTERNAL_AND_CLOUD_LOAD_BALANCING"
    ], var.ingress_type)
    error_message = "Ingress type must be one of: INGRESS_ALL, INGRESS_INTERNAL, INGRESS_INTERNAL_AND_CLOUD_LOAD_BALANCING."
  }
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access"
  type        = bool
  default     = false
}

variable "gateway_service_account" {
  description = "Service account email for API Gateway access"
  type        = string
  default     = null
}

variable "env_vars" {
  description = "Environment variables"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Environment variables from Secret Manager"
  type = map(object({
    secret_name = string
    version     = string
  }))
  default = {}
}

variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/healthz"
}

variable "startup_probe_initial_delay" {
  description = "Startup probe initial delay in seconds"
  type        = number
  default     = 10
}

variable "startup_probe_timeout" {
  description = "Startup probe timeout in seconds"
  type        = number
  default     = 5
}

variable "startup_probe_period" {
  description = "Startup probe period in seconds"
  type        = number
  default     = 10
}

variable "startup_probe_failure_threshold" {
  description = "Startup probe failure threshold"
  type        = number
  default     = 3
}

variable "liveness_probe_initial_delay" {
  description = "Liveness probe initial delay in seconds"
  type        = number
  default     = 30
}

variable "liveness_probe_timeout" {
  description = "Liveness probe timeout in seconds"
  type        = number
  default     = 5
}

variable "liveness_probe_period" {
  description = "Liveness probe period in seconds"
  type        = number
  default     = 30
}

variable "liveness_probe_failure_threshold" {
  description = "Liveness probe failure threshold"
  type        = number
  default     = 3
}

variable "vpc_connector_name" {
  description = "VPC connector name for private networking"
  type        = string
  default     = null
}

variable "vpc_egress" {
  description = "VPC egress setting"
  type        = string
  default     = "ALL_TRAFFIC"
  validation {
    condition = contains([
      "ALL_TRAFFIC",
      "PRIVATE_RANGES_ONLY"
    ], var.vpc_egress)
    error_message = "VPC egress must be either ALL_TRAFFIC or PRIVATE_RANGES_ONLY."
  }
}

# Feature flags for IAM permissions
variable "enable_secret_manager" {
  description = "Enable Secret Manager access"
  type        = bool
  default     = false
}

variable "enable_pubsub" {
  description = "Enable Pub/Sub publishing"
  type        = bool
  default     = false
}

variable "enable_firestore" {
  description = "Enable Firestore access"
  type        = bool
  default     = false
}

variable "enable_storage" {
  description = "Enable Cloud Storage access"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}
