# Dockerized OAuth 1.0a Sandbox Server

A standalone, Dockerized OAuth 1.0a Provider designed for debugging and testing clients.

It features **"Nuclear Debug Logging"** to help you solve signature mismatches by printing the exact Base String the server is expecting.

## Features
-  **Full Docker Support:** One command to run.
-  **Auto-Generated SSL:** Automatically creates valid-for-100-years self-signed certs on startup.
-  **Replay Protection:** Sophisticated nonce/timestamp validation.
-  **Debug Logs:** Prints decrypted headers and signature base strings.

## Quick Start

### 1. Run via Docker
```bash
docker build -t oauth1-server .
docker run -p 9090:9090 oauth1-server
```
