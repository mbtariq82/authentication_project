#!/bin/bash
set -euxo pipefail

# Update system
apt-get update
apt-get install -y docker.io

# Enable Docker
systemctl enable --now docker
usermod -aG docker azureuser

# Create app directory
mkdir -p /opt/authentication-project
