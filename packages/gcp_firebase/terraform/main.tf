# =========================
# Living Twin Infrastructure - Main Configuration
# =========================

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Local values for common configuration
locals {
  environment = terraform.workspace
  
  # Common labels
  common_labels = {
    project     = "living-twin"
    environment = local.environment
    managed-by  = "terraform"
    workspace   = terraform.workspace
  }
  
  # Environment-specific configuration
  env_config = {
    dev = {
      min_instances = 0
      max_instances = 5
      cpu_limit     = "1000m"
      memory_limit  = "2Gi"
      enable_dlq    = true
      enable_backup = false
    }
    staging = {
      min_instances = 1
      max_instances = 10
      cpu_limit     = "1000m"
      memory_limit  = "2Gi"
      enable_dlq    = true
      enable_backup = true
    }
    prod = {
      min_instances = 2
      max_instances = 50
      cpu_limit     = "2000m"
      memory_limit  = "4Gi"
      enable_dlq    = true
      enable_backup = true
    }
  }
  
  current_env = local.env_config[local.environment]
  
  # Service configuration
  services = {
    api = {
      name         = "living-twin-api-${local.environment}"
      image_url    = var.api_image_url
      port         = 8000
      health_path  = "/healthz"
    }
    worker = {
      name         = "living-twin-worker-${local.environment}"
      image_url    = var.worker_image_url
      port         = 8080
      health_path  = "/health"
    }
  }
  
  # Pub/Sub topics configuration
  pubsub_topics = {
    "living-twin-events" = {
      labels = merge(local.common_labels, { purpose = "main-events" })
      iam_bindings = [
        {
          role   = "roles/pubsub.publisher"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
      subscription_iam_bindings = []
    }
    "living-twin-document-events" = {
      labels = merge(local.common_labels, { purpose = "document-events" })
      iam_bindings = [
        {
          role   = "roles/pubsub.publisher"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
      subscription_iam_bindings = [
        {
          role   = "roles/pubsub.subscriber"
          member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
        }
      ]
    }
    "living-twin-query-events" = {
      labels = merge(local.common_labels, { purpose = "query-events" })
      iam_bindings = [
        {
          role   = "roles/pubsub.publisher"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
      subscription_iam_bindings = [
        {
          role   = "roles/pubsub.subscriber"
          member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
        }
      ]
    }
    "living-twin-user-events" = {
      labels = merge(local.common_labels, { purpose = "user-events" })
      iam_bindings = [
        {
          role   = "roles/pubsub.publisher"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
      subscription_iam_bindings = []
    }
    "living-twin-system-events" = {
      labels = merge(local.common_labels, { purpose = "system-events" })
      iam_bindings = [
        {
          role   = "roles/pubsub.publisher"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
      subscription_iam_bindings = []
    }
  }
  
  # Secrets configuration
  secrets_config = {
    "openai-api-key" = {
      secret_data = var.openai_api_key
      labels      = merge(local.common_labels, { purpose = "llm-api" })
      iam_bindings = [
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
    }
    "neo4j-uri" = {
      secret_data = var.neo4j_uri
      labels      = merge(local.common_labels, { purpose = "database" })
      iam_bindings = [
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        },
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
        }
      ]
    }
    "neo4j-user" = {
      secret_data = var.neo4j_user
      labels      = merge(local.common_labels, { purpose = "database" })
      iam_bindings = [
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        },
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
        }
      ]
    }
    "neo4j-password" = {
      secret_data = var.neo4j_password
      labels      = merge(local.common_labels, { purpose = "database" })
      iam_bindings = [
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        },
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
        }
      ]
    }
    "firebase-service-account-key" = {
      secret_data = var.firebase_service_account_key
      labels      = merge(local.common_labels, { purpose = "auth" })
      iam_bindings = [
        {
          role   = "roles/secretmanager.secretAccessor"
          member = "serviceAccount:${module.cloud_run_api.service_account_email}"
        }
      ]
    }
  }
}

# =========================
# Pub/Sub Module
# =========================
module "pubsub" {
  source = "./modules/pubsub"
  
  project_id = var.project_id
  topics     = local.pubsub_topics
  
  enable_dlq                = local.current_env.enable_dlq
  create_base_subscriptions = true
  create_service_account    = true
  service_account_prefix    = "living-twin-${local.environment}"
  
  labels = local.common_labels
}

# =========================
# Secret Manager Module
# =========================
module "secret_manager" {
  source = "./modules/secret_manager"
  
  project_id = var.project_id
  secrets    = local.secrets_config
  
  environment               = local.environment
  create_service_account    = true
  service_account_prefix    = "living-twin-${local.environment}"
  enable_monitoring         = true
  enable_backup            = local.current_env.enable_backup
  
  labels = local.common_labels
}

# =========================
# Cloud Run API Service
# =========================
module "cloud_run_api" {
  source = "./modules/cloud_run"
  
  project_id    = var.project_id
  region        = var.region
  service_name  = local.services.api.name
  image_url     = local.services.api.image_url
  
  container_port = local.services.api.port
  cpu_limit      = local.current_env.cpu_limit
  memory_limit   = local.current_env.memory_limit
  min_instances  = local.current_env.min_instances
  max_instances  = local.current_env.max_instances
  
  health_check_path = local.services.api.health_path
  
  allow_unauthenticated = local.environment != "prod"
  
  # Environment variables
  env_vars = {
    ENVIRONMENT = local.environment
    PROJECT_ID  = var.project_id
    REGION      = var.region
  }
  
  # Secret environment variables
  secret_env_vars = {
    OPENAI_API_KEY = {
      secret_name = module.secret_manager.secret_names["openai-api-key"]
      version     = "latest"
    }
    NEO4J_URI = {
      secret_name = module.secret_manager.secret_names["neo4j-uri"]
      version     = "latest"
    }
    NEO4J_USER = {
      secret_name = module.secret_manager.secret_names["neo4j-user"]
      version     = "latest"
    }
    NEO4J_PASSWORD = {
      secret_name = module.secret_manager.secret_names["neo4j-password"]
      version     = "latest"
    }
    FIREBASE_SERVICE_ACCOUNT_KEY = {
      secret_name = module.secret_manager.secret_names["firebase-service-account-key"]
      version     = "latest"
    }
  }
  
  # Enable integrations
  enable_secret_manager = true
  enable_pubsub        = true
  enable_firestore     = true
  enable_storage       = true
  
  labels = local.common_labels
  
  depends_on = [
    module.secret_manager,
    module.pubsub
  ]
}

# =========================
# Cloud Run Worker Service
# =========================
module "cloud_run_worker" {
  source = "./modules/cloud_run"
  
  project_id    = var.project_id
  region        = var.region
  service_name  = local.services.worker.name
  image_url     = local.services.worker.image_url
  
  container_port = local.services.worker.port
  cpu_limit      = local.current_env.cpu_limit
  memory_limit   = local.current_env.memory_limit
  min_instances  = 0  # Workers scale to zero
  max_instances  = local.current_env.max_instances
  
  health_check_path = local.services.worker.health_path
  
  allow_unauthenticated = false  # Workers are internal
  
  # Environment variables
  env_vars = {
    ENVIRONMENT = local.environment
    PROJECT_ID  = var.project_id
    REGION      = var.region
  }
  
  # Secret environment variables
  secret_env_vars = {
    NEO4J_URI = {
      secret_name = module.secret_manager.secret_names["neo4j-uri"]
      version     = "latest"
    }
    NEO4J_USER = {
      secret_name = module.secret_manager.secret_names["neo4j-user"]
      version     = "latest"
    }
    NEO4J_PASSWORD = {
      secret_name = module.secret_manager.secret_names["neo4j-password"]
      version     = "latest"
    }
  }
  
  # Enable integrations
  enable_secret_manager = true
  enable_pubsub        = true
  enable_firestore     = true
  
  labels = local.common_labels
  
  depends_on = [
    module.secret_manager,
    module.pubsub
  ]
}

# =========================
# Cloud Storage Buckets
# =========================
resource "google_storage_bucket" "document_storage" {
  name     = "${var.project_id}-documents-${local.environment}"
  location = var.region
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  labels = merge(local.common_labels, {
    purpose = "document-storage"
  })
}

resource "google_storage_bucket" "backup_storage" {
  count = local.current_env.enable_backup ? 1 : 0
  
  name     = "${var.project_id}-backups-${local.environment}"
  location = var.region
  project  = var.project_id
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
  
  labels = merge(local.common_labels, {
    purpose = "backup-storage"
  })
}

# =========================
# IAM Bindings for Storage
# =========================
resource "google_storage_bucket_iam_member" "api_document_access" {
  bucket = google_storage_bucket.document_storage.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${module.cloud_run_api.service_account_email}"
}

resource "google_storage_bucket_iam_member" "worker_document_access" {
  bucket = google_storage_bucket.document_storage.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.cloud_run_worker.service_account_email}"
}

# =========================
# Firestore Indexes (if needed)
# =========================
resource "google_firestore_index" "tenant_documents" {
  project    = var.project_id
  collection = "documents"
  
  fields {
    field_path = "tenant_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "tenant_users" {
  project    = var.project_id
  collection = "users"
  
  fields {
    field_path = "tenant_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "email"
    order      = "ASCENDING"
  }
}
