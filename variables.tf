####################
### GOOGLE CLOUD ###
####################
variable "gcloud_credentials_file" {
  default = "~/.gcloud/cloudflare.json"
}

variable "gce_ssh_username" {
  default = "pdonahue"
}

variable "gce_ssh_pubkey_file" {
  default = "~/.ssh/gcloud.pub"
}

variable "gcloud_project" {
  default = "prdtest-dnsfw"
}

variable "gcloud_region" {
  default = "us-west1"
}

variable "gcloud_zone" {
  default = "us-west1-b"
}

variable "gcloud_machine_type" {
  default = "n1-highcpu-8"
}

variable "gcloud_image" {
  default = "debian-cloud/debian-9"
}

variable "gcloud_image_size" {
  default = "256"
}

variable "setup_script" {
  default = "setup.sh"
}
