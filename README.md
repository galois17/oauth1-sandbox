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

##  Running the Sample Clients

This repository includes working clients for Ruby and Python to help you test the server immediately.

### Option A: Ruby Client
This client is pre-configured to handle the self-signed SSL certificate automatically.

```bash
cd clients/ruby
bundle install
ruby client.rb
```

### Option B: Python Client
A simple requests-based client that demonstrates how to suppress SSL warnings for local development.

```bash
cd clients/python
pip install -r requirements.txt
python client.py

```

## See It In Action

Here is an actual run of the Ruby client against the Docker server.

Notice how the **Server Logs** (top) print the exact incoming headers and signature verification steps—this is the "Nuclear Debugging" feature that makes fixing client bugs easy.

### 1. Server Output (Docker Logs)
```text
==================================================
      INCOMING POST REQUEST
==================================================
URL:     https://127.0.0.1.nip.io:9090/oauth/access_token
Headers: {'accept-encoding': 'gzip;q=1.0,deflate;q=0.6,identity;q=0.3', 'accept': '*/*', 'user-agent': 'OAuth gem v1.1.3', 'content-length': '0', 'Authorization': 'OAuth oauth_consumer_key="ClientKeyMustBeLongEnough00001", oauth_nonce="891MkTg6Yigf2ruZzZ0LlYYPzv1NtOtOfGzODq4PRw", oauth_signature="rM3vYS5kg7P8hGdderS6Vx%2FIFVg%3D", oauth_signature_method="HMAC-SHA1", oauth_timestamp="1768078757", oauth_token="BxmQenbHjYK7Mm8PREES8bqyMd3YXA", oauth_verifier="804209", oauth_version="1.0"', 'connection': 'close', 'host': '127.0.0.1.nip.io:9090'}
Body:
==================================================

[DEBUG] check_nonce: '891MkTg6Yigf2ruZzZ0LlYYPzv1NtOtOfGzODq4PRw' -> ALLOWED
[DEBUG] check_verifier: '804209' -> ALLOWED
[DEBUG] Validating Verifier: Client says '804209' vs Stored '804209'
[STORE] Issuing Access Token: {'oauth_token': 'CVmmJ9f3hUq7zGhvC3ORTltvMKCvvH', 'oauth_token_secret': 'ZhpJogoM43W0BWwtCTLz8D6kqEYSKe', 'oauth_authorized_realms': ''}
[STORE] Invalidating (Burning) Request Token: BxmQenbHjYK7Mm8PREES8bqyMd3YXA
INFO:     192.168.65.1:26189 - "POST /oauth/access_token HTTP/1.1" 200 OK
```

### 2. Client Output (Ruby)

```text
--- RUBY CLIENT (FULL FLOW) ---
Target: https://127.0.0.1.nip.io:9090

[STEP 1] Requesting Temporary Token...
   > Token:  BxmQenbHjYK7Mm8PREES8bqyMd3YXA
   > Secret: 3YMxYoeaYoSq7mC1qlQOeZ2D6HJ9Tr

[STEP 2] User Authorization
   > ---------------------------------------------------------
   > OPEN THIS URL IN YOUR BROWSER:
   > https://127.0.0.1.nip.io:9090/oauth/authorize?oauth_token=BxmQenbHjYK7Mm8PREES8bqyMd3YXA
   > ---------------------------------------------------------
   (The server will show you a 6-digit PIN code. Enter it below.)
   > PIN Code: 804209

[STEP 3] Exchanging for Access Token...

[SUCCESS] 🚀 OAuth Flow Complete!
   > FINAL Access Token:  CVmmJ9f3hUq7zGhvC3ORTltvMKCvvH
   > FINAL Access Secret: ZhpJogoM43W0BWwtCTLz8D6kqEYSKe
   > You can now use this token to access protected API endpoints.
```
=======
## License
This project is open source and available under the [MIT License](LICENSE).

