# Dockerized OAuth 1.0a Sandbox Server

Oauth 1.0a is notoriously hard to play with as there are limited public APIs available these days (many moved to Oauth2) and it's hard to get the credentials exactly right. It's still widely used with private/legacy APIs.

This is a standalone, Dockerized OAuth 1.0a Provider designed for debugging and testing clients.

I went crazy with Debug Logging to help you solve signature mismatches by printing the exact Base String the server is expecting.

## Features
-  **Full Docker Support:** One command to run.
-  **Auto-Generated SSL:** Automatically creates valid-for-100-years self-signed certs on startup.
-  **Replay Protection:** Sophisticated nonce/timestamp validation.
-  **Debug Logs:** Prints decrypted headers and signature base strings.

## Quick Start

### 1. Run via Docker
```bash
# Build the image
docker build -t oauth1-server .

# Run it (Mapping port 9090)
docker run --rm -p 9090:9090 oauth1-server
```

Once running, the server is available at:

https://127.0.0.1.nip.io:9090

(Note: We use nip.io to force DNS resolution to localhost while appearing as a "real" domain to satisfy strict OAuth libraries.)

#### The client key and secret is hardcoded with these example values. I will move it out at a later time-- e.g., pass the client key and secret as an argument when running the docker image
```bash
CLIENT_KEY =    "ClientKeyMustBeLongEnough00001" 
CLIENT_SECRET = "ClientSecretMustBeLongEnough01"
```


## License
This project is open source and available under the [MIT License](LICENSE).
