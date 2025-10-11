#!/bin/bash
# This StackScript installs git, Docker, Docker Compose, Portainer (in a container),
# clones both backend and frontend repositories, creates a shared network, and runs docker compose.

# <UDF name="app_repository" label="Application Git Repository URL" example="https://github.com/user/repo.git" />
# Define the application repository URLs as variables
# APP_REPOSITORY="https://github.com/alphabet-ai-inc/authserver"
# FRONTEND_REPOSITORY="https://github.com/alphabet-ai-inc/authserver_front_end"

# Exit on error
set -e

# Set non-interactive frontend for apt
export DEBIAN_FRONTEND=noninteractive

# Update system and install prerequisites
apt-get update -y
apt-get install -y curl ca-certificates gnupg-agent software-properties-common wget

# Install git
apt-get install -y git

# Install Docker
curl -fsSL get.docker.com -o get-docker.sh && chmod +x get-docker.sh && ./get-docker.sh

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Add user to docker group
usermod -aG docker $(whoami)

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

apt-get install -y jq netcat-openbsd

# Run Portainer in a container
docker run -d \
    --name portainer \
    --restart always \
    -p 9000:9000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest

# Read apps from /tmp/apps.json
if [ ! -f "/tmp/apps.json" ]; then
  echo "Error: /tmp/apps.json not found"
  exit 1
fi
mapfile -t apps < <(jq -c '.[]' /tmp/apps.json)

# Process each application
for app in "${apps[@]}"; do
  name=$(echo "$app" | jq -r '.name')
  url=$(echo "$app" | jq -r '.url')
  directory=$(echo "$app" | jq -r '.directory')
  
  echo "Processing app: $name"
  echo "Cloning $url to $directory"
  
  mkdir -p "$directory"
  git clone "$url" "$directory"
  
  # Copy .env from /tmp to application directory
  env_file="/tmp/${name}.${ENV}.env"
  if [ -f "$env_file" ]; then
    echo "Copying $env_file to $directory/.env"
    cp "$env_file" "$directory/.env"
    chmod 600 "$directory/.env"
  else
    echo "Error: .env file $env_file not found"
    exit 1
  fi
  
  # Execute commands
  cd "$directory"
  echo "Executing commands in $directory"
  commands=$(echo "$app" | jq -r '.commands[]')
  while IFS= read -r cmd; do
    echo "Running: $cmd"
    bash -c "$cmd" || { echo "Command failed: $cmd"; exit 1; }
  done <<< "$commands"
done

# Clean up
apt-get autoclean
apt-get autoremove --purge -y

# Log completion
echo "StackScript completed: Git, Docker, Portainer, and applications deployed."