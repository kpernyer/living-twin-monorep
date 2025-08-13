# =========================
# Production Environment Configuration
# =========================

# Production settings - performance and reliability first
api_min_instances = 2      # Always keep 2 instances running for HA
api_max_instances = 20     # Scale up to handle production traffic
worker_min_instances = 1   # Keep 1 worker always ready
worker_max_instances = 15  # Scale workers for production workload

# Enable all production features
enable_backup = true
enable_monitoring = true
enable_audit_logs = true

# Production settings
enable_debug_mode = false
log_level = "INFO"

# Production notification channels (add your actual channels)
notification_channels = [
  # "projects/YOUR_PROJECT/notificationChannels/YOUR_CHANNEL_ID"
]

# Production optimization
backup_retention_days = 90  # Longer retention for compliance
auto_scaling_target_cpu = 60  # Lower threshold = more responsive scaling

# Production overrides
environment_overrides = {
  prod = {
    min_instances = 2        # High availability
    max_instances = 20
    cpu_limit = "2000m"      # More CPU for performance
    memory_limit = "4Gi"     # More memory for caching
    enable_backup = true
    enable_monitoring = true
  }
}

# Labels for cost tracking and compliance
additional_labels = {
  environment = "production"
  cost-center = "operations"
  compliance = "required"
  backup = "enabled"
}

# Production-specific features
enable_preemptible_workers = false  # Use reliable instances
max_concurrent_requests = 80        # Higher concurrency
api_timeout_seconds = 300           # Standard timeout
worker_timeout_seconds = 7200       # 2 hours for production tasks

# Production features
enable_bigquery = false      # Enable for analytics if needed
enable_redis = false         # Enable for caching if needed
enable_cloud_sql = false     # Enable for relational data if needed

# Security and compliance
enable_binary_authorization = false  # Enable for container security
enable_workload_identity = false     # Enable for GKE integration
data_residency_region = "europe-west1"  # EU data residency

# Disaster recovery
enable_cross_region_backup = true
disaster_recovery_region = "europe-west3"

# Custom domain (configure if you have one)
# custom_domain = "api.yourdomain.com"
# ssl_certificate_name = "your-ssl-cert"

# API Gateway (enable if needed)
enable_api_gateway = false
