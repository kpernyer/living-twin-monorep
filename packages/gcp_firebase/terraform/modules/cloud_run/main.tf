# =========================
# Cloud Run Module
# =========================

resource "google_service_account" "run_sa" {
  account_id   = "${var.service_name}-run-sa"
  display_name = "${var.service_name} Cloud Run SA"
  project      = var.project_id
}

resource "google_project_iam_member" "run_sa_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "run_sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "run_sa_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Additional IAM for Secret Manager access
resource "google_project_iam_member" "run_sa_secret_accessor" {
  count   = var.enable_secret_manager ? 1 : 0
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Additional IAM for Pub/Sub publishing
resource "google_project_iam_member" "run_sa_pubsub_publisher" {
  count   = var.enable_pubsub ? 1 : 0
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Additional IAM for Firestore access
resource "google_project_iam_member" "run_sa_firestore" {
  count   = var.enable_firestore ? 1 : 0
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Additional IAM for Cloud Storage access
resource "google_project_iam_member" "run_sa_storage" {
  count   = var.enable_storage ? 1 : 0
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.run_sa.email
    
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
    
    containers {
      image = var.image_url
      
      ports {
        container_port = var.container_port
      }
      
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
        cpu_idle = var.cpu_idle
      }
      
      # Environment variables from variables
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }
      
      # Environment variables from secrets
      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret_name
              version = env.value.version
            }
          }
        }
      }
      
      # Startup probe
      startup_probe {
        http_get {
          path = var.health_check_path
          port = var.container_port
        }
        initial_delay_seconds = var.startup_probe_initial_delay
        timeout_seconds       = var.startup_probe_timeout
        period_seconds        = var.startup_probe_period
        failure_threshold     = var.startup_probe_failure_threshold
      }
      
      # Liveness probe
      liveness_probe {
        http_get {
          path = var.health_check_path
          port = var.container_port
        }
        initial_delay_seconds = var.liveness_probe_initial_delay
        timeout_seconds       = var.liveness_probe_timeout
        period_seconds        = var.liveness_probe_period
        failure_threshold     = var.liveness_probe_failure_threshold
      }
    }
    
    timeout = "${var.request_timeout}s"
    
    # VPC connector if specified
    dynamic "vpc_access" {
      for_each = var.vpc_connector_name != null ? [1] : []
      content {
        connector = var.vpc_connector_name
        egress    = var.vpc_egress
      }
    }
  }
  
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
  
  ingress = var.ingress_type
  
  depends_on = [
    google_project_iam_member.run_sa_logging,
    google_project_iam_member.run_sa_monitoring,
    google_project_iam_member.run_sa_trace
  ]
}

# IAM for public access if enabled
resource "google_cloud_run_service_iam_member" "public_access" {
  count    = var.allow_unauthenticated ? 1 : 0
  location = google_cloud_run_v2_service.service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM for API Gateway access if specified
resource "google_cloud_run_service_iam_member" "gateway_access" {
  count    = var.gateway_service_account != null ? 1 : 0
  location = google_cloud_run_v2_service.service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.gateway_service_account}"
}
