# =========================
# Pub/Sub Module Outputs
# =========================

output "topic_names" {
  description = "Names of created topics"
  value       = { for k, v in google_pubsub_topic.topics : k => v.name }
}

output "topic_ids" {
  description = "IDs of created topics"
  value       = { for k, v in google_pubsub_topic.topics : k => v.id }
}

output "dlq_topic_names" {
  description = "Names of created DLQ topics"
  value       = { for k, v in google_pubsub_topic.dlq_topics : k => v.name }
}

output "dlq_topic_ids" {
  description = "IDs of created DLQ topics"
  value       = { for k, v in google_pubsub_topic.dlq_topics : k => v.id }
}

output "subscription_names" {
  description = "Names of created base subscriptions"
  value       = { for k, v in google_pubsub_subscription.base_subscriptions : k => v.name }
}

output "subscription_ids" {
  description = "IDs of created base subscriptions"
  value       = { for k, v in google_pubsub_subscription.base_subscriptions : k => v.id }
}

output "service_account_email" {
  description = "Email of the Pub/Sub service account"
  value       = var.create_service_account ? google_service_account.pubsub_sa[0].email : null
}

output "service_account_id" {
  description = "ID of the Pub/Sub service account"
  value       = var.create_service_account ? google_service_account.pubsub_sa[0].id : null
}

output "service_account_name" {
  description = "Name of the Pub/Sub service account"
  value       = var.create_service_account ? google_service_account.pubsub_sa[0].name : null
}

output "schema_names" {
  description = "Names of created schemas"
  value       = { for k, v in google_pubsub_schema.schemas : k => v.name }
}

output "schema_ids" {
  description = "IDs of created schemas"
  value       = { for k, v in google_pubsub_schema.schemas : k => v.id }
}

# Outputs for CI/CD integration
output "topic_publish_urls" {
  description = "URLs for publishing to topics (for CI/CD)"
  value = {
    for k, v in google_pubsub_topic.topics : k => "projects/${var.project_id}/topics/${v.name}"
  }
}

output "subscription_pull_urls" {
  description = "URLs for pulling from subscriptions (for CI/CD)"
  value = {
    for k, v in google_pubsub_subscription.base_subscriptions : k => "projects/${var.project_id}/subscriptions/${v.name}"
  }
}

# Outputs for monitoring and alerting
output "topic_monitoring_labels" {
  description = "Labels for topic monitoring"
  value = {
    for k, v in google_pubsub_topic.topics : k => v.labels
  }
}

output "dlq_monitoring_labels" {
  description = "Labels for DLQ monitoring"
  value = {
    for k, v in google_pubsub_topic.dlq_topics : k => v.labels
  }
}

# Outputs for application configuration
output "topic_config" {
  description = "Topic configuration for application use"
  value = {
    for k, v in google_pubsub_topic.topics : k => {
      name                       = v.name
      id                        = v.id
      project                   = var.project_id
      dlq_topic                 = var.enable_dlq ? google_pubsub_topic.dlq_topics[k].name : null
      message_retention_duration = v.message_retention_duration
    }
  }
}

output "subscription_config" {
  description = "Subscription configuration for application use"
  value = {
    for k, v in google_pubsub_subscription.base_subscriptions : k => {
      name                       = v.name
      id                        = v.id
      topic                     = v.topic
      ack_deadline_seconds      = v.ack_deadline_seconds
      message_retention_duration = v.message_retention_duration
      max_delivery_attempts     = var.enable_dlq ? var.max_delivery_attempts : null
    }
  }
}

# Outputs for Terraform state management
output "all_topic_names" {
  description = "All topic names including DLQ topics"
  value = concat(
    [for v in google_pubsub_topic.topics : v.name],
    [for v in google_pubsub_topic.dlq_topics : v.name]
  )
}

output "all_subscription_names" {
  description = "All subscription names"
  value = [for v in google_pubsub_subscription.base_subscriptions : v.name]
}

# Outputs for IAM and security
output "topic_iam_bindings" {
  description = "Topic IAM bindings applied"
  value = {
    for binding in local.topic_iam_bindings : "${binding.topic}-${binding.role}" => {
      topic  = binding.topic
      role   = binding.role
      member = binding.member
    }
  }
}

output "subscription_iam_bindings" {
  description = "Subscription IAM bindings applied"
  value = {
    for binding in local.subscription_iam_bindings : "${binding.subscription}-${binding.role}" => {
      subscription = binding.subscription
      role         = binding.role
      member       = binding.member
    }
  }
}

# Outputs for integration with other modules
output "publisher_service_accounts" {
  description = "Service accounts with publisher permissions"
  value = var.create_service_account ? [google_service_account.pubsub_sa[0].email] : []
}

output "subscriber_service_accounts" {
  description = "Service accounts with subscriber permissions"
  value = var.create_service_account ? [google_service_account.pubsub_sa[0].email] : []
}

# Outputs for environment-specific configuration
output "environment_config" {
  description = "Environment-specific Pub/Sub configuration"
  value = {
    project_id                    = var.project_id
    topics                       = { for k, v in google_pubsub_topic.topics : k => v.name }
    dlq_topics                   = { for k, v in google_pubsub_topic.dlq_topics : k => v.name }
    subscriptions               = { for k, v in google_pubsub_subscription.base_subscriptions : k => v.name }
    service_account_email       = var.create_service_account ? google_service_account.pubsub_sa[0].email : null
    message_retention_duration  = var.message_retention_duration
    ack_deadline_seconds       = var.ack_deadline_seconds
    max_delivery_attempts      = var.max_delivery_attempts
    enable_dlq                 = var.enable_dlq
  }
}
