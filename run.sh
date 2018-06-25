#!/bin/bash

terraform init -upgrade
terraform apply --auto-approve

export PROBEIP=$(terraform state show google_compute_instance.probe|grep assigned_nat_ip|awk '{print $3}')
ssh-add  ~/.ssh/gcloud

# ssh -oStrictHostKeyChecking=no -i ~/.ssh/gcloud $PROBEIP
