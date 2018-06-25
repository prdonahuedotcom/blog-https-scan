####################
### GOOGLE CLOUD ###
####################
provider "google" {
  region      = "${var.gcloud_region}"
  project     = "${var.gcloud_project}"
  credentials = "${file(var.gcloud_credentials_file)}"
}

resource "google_compute_instance" "probe" {
  name         = "probe"
  zone         = "${var.gcloud_zone}"
  machine_type = "${var.gcloud_machine_type}"

  tags = ["probe"]

  network_interface {
    network = "default"

    access_config {}
  }

  boot_disk {
    initialize_params {
      image = "${var.gcloud_image}"
      size  = "${var.gcloud_image_size}"
    }
  }

  metadata {
    sshKeys  = "${var.gce_ssh_username}:${file(var.gce_ssh_pubkey_file)}"
    username = "${var.gce_ssh_username}"
  }

  metadata_startup_script = "${file(var.setup_script)}"
}
