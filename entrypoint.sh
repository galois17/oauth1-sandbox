#!/bin/bash
set -e

# Define where we expect certificates to live
CERT_DIR="/app/certs"
KEY_FILE="$CERT_DIR/key.pem"
CERT_FILE="$CERT_DIR/cert.pem"

# Create directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist (e.g., mounted via volume)
if [ -f "$KEY_FILE" ] && [ -f "$CERT_FILE" ]; then
    echo "--- [ENTRYPOINT] Found existing certificates in $CERT_DIR. Using them. ---"
else
    echo "--- [ENTRYPOINT] No certificates found. Generating ephemeral self-signed keys... ---"
    
    # Generate a cert valid for 100 years (36500 days)
    # This prevents 'expired certificate' errors in dev environments
    openssl req -x509 -newkey rsa:4096 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -days 36500 \
        -nodes \
        -subj '/CN=127.0.0.1.nip.io'
        
    echo "--- [ENTRYPOINT] Certificates generated successfully. ---"
fi

# Execute the command passed to docker (or the default CMD)
exec "$@"