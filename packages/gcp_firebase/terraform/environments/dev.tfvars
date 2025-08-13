# =========================
# Development Environment Configuration
# =========================

# Cost-optimized settings for development
api_min_instances = 0      # Scale to zero when not used
api_max_instances = 3      # Limit maximum scale
worker_min_instances = 0   # Workers scale to zero
worker_max_instances = 2   # Limited worker scaling

# Disable expensive features for dev
enable_backup = false
enable_monitoring = true   # Keep monitoring for debugging
enable_audit_logs = false # Reduce log costs

# Development-specific settings
enable_debug_mode = true
log_level = "DEBUG"

# Notification settings (optional)
notification_channels = []

# Cost optimization
backup_retention_days = 7  # Shorter retention
auto_scaling_target_cpu = 80  # Higher threshold = less scaling

# Development overrides
environment_overrides = {
  dev = {
    min_instances = 0
    max_instances = 3
    cpu_limit = "1000m"
    memory_limit = "1Gi"      # Reduced memory for cost savings
    enable_backup = false
    enable_monitoring = true
  }
}

# Labels for cost tracking
additional_labels = {
  environment = "development"
  cost-center = "engineering"
  auto-shutdown = "enabled"
}

# Development-specific features
enable_preemptible_workers = true  # Use cheaper preemptible instances
max_concurrent_requests = 40       # Lower concurrency for dev
api_timeout_seconds = 120          # Shorter timeout
worker_timeout_seconds = 1800      # 30 minutes for dev tasks
