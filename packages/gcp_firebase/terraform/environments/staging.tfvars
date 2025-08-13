# =========================
# Staging Environment Configuration
# =========================

# Balanced settings for staging - performance testing with cost awareness
api_min_instances = 0      # Can scale to zero for cost savings
api_max_instances = 8      # Higher scale for load testing
worker_min_instances = 0   # Workers scale to zero
worker_max_instances = 5   # More workers for testing

# Enable features for testing
enable_backup = true       # Test backup functionality
enable_monitoring = true   # Full monitoring
enable_audit_logs = true   # Test audit logging

# Staging-specific settings
enable_debug_mode = false
log_level = "INFO"

# Notification settings
notification_channels = []  # Add your notification channels here

# Moderate cost optimization
backup_retention_days = 30
auto_scaling_target_cpu = 70  # Moderate scaling threshold

# Staging overrides
environment_overrides = {
  staging = {
    min_instances = 0        # Scale to zero for cost savings
    max_instances = 8
    cpu_limit = "1000m"
    memory_limit = "2Gi"
    enable_backup = true
    enable_monitoring = true
  }
}

# Labels for cost tracking
additional_labels = {
  environment = "staging"
  cost-center = "engineering"
  purpose = "testing"
}

# Staging-specific features
enable_preemptible_workers = true  # Still use cheaper instances
max_concurrent_requests = 60       # Moderate concurrency
api_timeout_seconds = 300          # Standard timeout
worker_timeout_seconds = 3600      # 1 hour for staging tasks

# Testing features
enable_bigquery = false    # Enable if you need analytics testing
enable_redis = false       # Enable if you need caching testing
