#!/bin/bash

# Check DNS-propagation and run Caddy
# Get DOMAIN and VM_IP from terraform outputs
# Usage: ./run_caddy.sh

set -e

echo "🌐 DOMAIN: $DOMAIN"
echo "💻 VM_IP:  $VM_IP"

# Check values
if [ -z "$DOMAIN" ] || [ -z "$VM_IP" ]; then
    echo "❌ Error: Unable to get DOMAIN or VM_IP from env variables"
    echo "   Verify that outputs.tf contains:"
    echo "   output \"domain\" { value = module.linode_domain.domain_name }"
    echo "   output \"ips\" { value = module.linode_instances.instance_ips }"
    exit 1
fi

# Replay settings
MAX_RETRIES=120  # max 1 hour
RETRY_INTERVAL=30  # seconds

echo "⏳ Waiting for DNS propagation: $DOMAIN -> $VM_IP..."

attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    resolved_ip=$(dig +short "$DOMAIN" | head -n 1 | tr -d '\n')

    if [ "$resolved_ip" = "$VM_IP" ]; then
        echo "✅ Success! $DOMAIN resolves to $VM_IP"
        echo "🚀 Starting Caddy..."
        docker compose -f caddy-compose.yaml up -d
        echo "✅ Caddy started! Check logs: docker logs django-landing-caddy"
        exit 0
    else
        echo "⏳ Attempt $attempt/$MAX_RETRIES: Resolved IP is '$resolved_ip' (expected $VM_IP). Retrying in $RETRY_INTERVAL seconds..."
        sleep $RETRY_INTERVAL
        attempt=$((attempt + 1))
    fi
done

echo "Error: Max retries reached. DNS propagation failed."
echo "   Current IP for ${DOMAIN} $(dig +short "$DOMAIN")"
exit 1