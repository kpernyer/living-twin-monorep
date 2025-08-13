# =========================
# Cloud Run Module Outputs
# =========================

output "service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.service.name
}

output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.service.uri
}

output "service_id" {
  description = "ID of the Cloud Run service"
  value       = google_cloud_run_v2_service.service.id
}

output "service_location" {
  description = "Location of the Cloud Run service"
  value       = google_cloud_run_v2_service.service.location
}

output "service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = google_service_account.run_sa.email
}

output "service_account_id" {
  description = "ID of the service account used by Cloud Run"
  value       = google_service_account.run_sa.id
}

output "service_account_name" {
  description = "Name of the service account used by Cloud Run"
  value       = google_service_account.run_sa.name
}

output "latest_ready_revision" {
  description = "Latest ready revision name"
  value       = google_cloud_run_v2_service.service.latest_ready_revision
}

output "latest_created_revision" {
  description = "Latest created revision name"
  value       = google_cloud_run_v2_service.service.latest_created_revision
}

output "generation" {
  description = "Generation of the service"
  value       = google_cloud_run_v2_service.service.generation
}

output "observed_generation" {
  description = "Observed generation of the service"
  value       = google_cloud_run_v2_service.service.observed_generation
}

output "conditions" {
  description = "Conditions of the service"
  value       = google_cloud_run_v2_service.service.conditions
}

output "terminal_condition" {
  description = "Terminal condition of the service"
  value       = google_cloud_run_v2_service.service.terminal_condition
}

output "traffic" {
  description = "Traffic allocation for the service"
  value       = google_cloud_run_v2_service.service.traffic
}

output "ingress" {
  description = "Ingress settings for the service"
  value       = google_cloud_run_v2_service.service.ingress
}

# Outputs for integration with other modules
output "invoker_members" {
  description = "Members with Cloud Run invoker permissions"
  value = concat(
    var.allow_unauthenticated ? ["allUsers"] : [],
    var.gateway_service_account != null ? ["serviceAccount:${var.gateway_service_account}"] : []
  )
}

output "service_fqdn" {
  description = "Fully qualified domain name of the service"
  value       = replace(google_cloud_run_v2_service.service.uri, "https://", "")
}

output "service_domain" {
  description = "Domain of the service (without protocol)"
  value       = replace(replace(google_cloud_run_v2_service.service.uri, "https://", ""), "/.*", "")
}
