# Use python 3.10 slim for a small image size
FROM python:3.10-slim

# Install OpenSSL (Required for entrypoint generation)
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
# (We install directly to keep the Dockerfile simple for this example)
RUN pip install --no-cache-dir fastapi uvicorn oauthlib requests-oauthlib

# Copy application code
COPY server.py .
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Create the certs directory so permissions are correct
RUN mkdir -p /app/certs

# Expose the port defined in server.py
EXPOSE 9090

# Set the Entrypoint to our script
ENTRYPOINT ["./entrypoint.sh"]

# Default command to run the server
CMD ["python", "server.py"]