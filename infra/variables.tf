variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  # Default region for all resources.
  default = "europe-west1"
}
