terraform {
  backend "gcs" {
    bucket = "living-twin-terraform-state"
    prefix = "terraform/state"
  }
}
