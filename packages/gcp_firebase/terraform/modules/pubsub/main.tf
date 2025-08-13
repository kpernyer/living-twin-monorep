# =========================
# Pub/Sub Module
# =========================

# Main topics
resource "google_pubsub_topic" "topics" {
  for_each = var.topics
  
  name    = each.key
  project = var.project_id
  
  message_retention_duration = var.message_retention_duration
  
  dynamic "message_storage_policy" {
    for_each = var.allowed_persistence_regions != null ? [1] : []
    content {
      allowed_persistence_regions = var.allowed_persistence_regions
    }
  }
  
  dynamic "schema_settings" {
    for_each = each.value.schema_name != null ? [1] : []
    content {
      schema   = each.value.schema_name
      encoding = each.value.schema_encoding
    }
  }
  
  labels = merge(var.labels, each.value.labels)
}

# Dead Letter Queue topics
resource "google_pubsub_topic" "dlq_topics" {
  for_each = var.enable_dlq ? var.topics : {}
  
  name    = "${each.key}-dlq"
  project = var.project_id
  
  message_retention_duration = var.dlq_message_retention_duration
  
  dynamic "message_storage_policy" {
    for_each = var.allowed_persistence_regions != null ? [1] : []
    content {
      allowed_persistence_regions = var.allowed_persistence_regions
    }
  }
  
  labels = merge(var.labels, each.value.labels, {
    purpose = "dead-letter-queue"
  })
}

# Base subscriptions for monitoring/debugging
resource "google_pubsub_subscription" "base_subscriptions" {
  for_each = var.create_base_subscriptions ? var.topics : {}
  
  name    = "${each.key}-monitor"
  topic   = google_pubsub_topic.topics[each.key].name
  project = var.project_id
  
  ack_deadline_seconds       = var.ack_deadline_seconds
  message_retention_duration = var.subscription_message_retention_duration
  retain_acked_messages      = var.retain_acked_messages
  
  expiration_policy {
    ttl = var.subscription_expiration_ttl
  }
  
  retry_policy {
    minimum_backoff = var.retry_minimum_backoff
    maximum_backoff = var.retry_maximum_backoff
  }
  
  dynamic "dead_letter_policy" {
    for_each = var.enable_dlq ? [1] : []
    content {
      dead_letter_topic     = google_pubsub_topic.dlq_topics[each.key].id
      max_delivery_attempts = var.max_delivery_attempts
    }
  }
  
  dynamic "push_config" {
    for_each = each.value.push_endpoint != null ? [1] : []
    content {
      push_endpoint = each.value.push_endpoint
      
      dynamic "oidc_token" {
        for_each = each.value.push_service_account != null ? [1] : []
        content {
          service_account_email = each.value.push_service_account
          audience             = each.value.push_audience
        }
      }
      
      attributes = each.value.push_attributes
    }
  }
  
  labels = merge(var.labels, each.value.labels, {
    purpose = "monitoring"
  })
}

# Service account for Pub/Sub operations
resource "google_service_account" "pubsub_sa" {
  count = var.create_service_account ? 1 : 0
  
  account_id   = "${var.service_account_prefix}-pubsub-sa"
  display_name = "Pub/Sub Service Account"
  project      = var.project_id
}

# IAM bindings for the service account
resource "google_project_iam_member" "pubsub_publisher" {
  count = var.create_service_account ? 1 : 0
  
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.pubsub_sa[0].email}"
}

resource "google_project_iam_member" "pubsub_subscriber" {
  count = var.create_service_account ? 1 : 0
  
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pubsub_sa[0].email}"
}

resource "google_project_iam_member" "pubsub_viewer" {
  count = var.create_service_account ? 1 : 0
  
  project = var.project_id
  role    = "roles/pubsub.viewer"
  member  = "serviceAccount:${google_service_account.pubsub_sa[0].email}"
}

# Additional IAM bindings for external service accounts
resource "google_pubsub_topic_iam_member" "topic_publishers" {
  for_each = {
    for binding in local.topic_iam_bindings : "${binding.topic}-${binding.member}" => binding
    if binding.role == "roles/pubsub.publisher"
  }
  
  project = var.project_id
  topic   = each.value.topic
  role    = each.value.role
  member  = each.value.member
}

resource "google_pubsub_subscription_iam_member" "subscription_subscribers" {
  for_each = {
    for binding in local.subscription_iam_bindings : "${binding.subscription}-${binding.member}" => binding
    if binding.role == "roles/pubsub.subscriber"
  }
  
  project      = var.project_id
  subscription = each.value.subscription
  role         = each.value.role
  member       = each.value.member
}

# Schemas for message validation
resource "google_pubsub_schema" "schemas" {
  for_each = var.schemas
  
  name       = each.key
  type       = each.value.type
  definition = each.value.definition
  project    = var.project_id
}

# Local values for IAM bindings
locals {
  topic_iam_bindings = flatten([
    for topic_name, topic_config in var.topics : [
      for binding in topic_config.iam_bindings : {
        topic  = topic_name
        role   = binding.role
        member = binding.member
      }
    ]
  ])
  
  subscription_iam_bindings = flatten([
    for topic_name, topic_config in var.topics : [
      for binding in topic_config.subscription_iam_bindings : {
        subscription = "${topic_name}-monitor"
        role         = binding.role
        member       = binding.member
      }
    ] if var.create_base_subscriptions
  ])
}
