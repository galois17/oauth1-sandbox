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
      INCOMING REQUEST (NUCLEAR DEBUG)
==================================================
URL (Internal):  [https://127.0.0.1.nip.io:9090/oauth/request_token](https://127.0.0.1.nip.io:9090/oauth/request_token)
Method:          POST
Headers:         {'accept-encoding': 'gzip;q=1.0,deflate;q=0.6,identity;q=0.3', 'accept': '*/*', 'user-agent': 'OAuth gem v1.1.3', 'Authorization': 'OAuth oauth_callback="oob", oauth_consumer_key="ClientKeyMustBeLongEnough00001", ...'}
Body:            ''
==================================================

[DEBUG] enforce_ssl check: True
[DEBUG] check_nonce: 'tT6alHRVKjgZCn3S853kuGOxax5rTlazcbgxjPunbc' -> ALLOWED (Format ignored)
[DEBUG] validate_timestamp_and_nonce: TS=1768065880 | Nonce=tT6alHRVKjgZCn3S853kuGOxax5rTlazcbgxjPunbc
[SEC] Timestamp & Nonce Valid. Cached.
[DEBUG] validate_client_key: 'ClientKeyMustBeLongEnough00001'
[DEBUG] validate_redirect_uri: oob
[DEBUG] get_client_secret for: ClientKeyMustBeLongEnough00001
[DEBUG] save_request_token: {'oauth_token': 'sG06Yas6dJeMKPSr15Xa8lPypHTE65', ...}
INFO:      192.168.65.1:36881 - "POST /oauth/request_token HTTP/1.1" 200 OK
```

### 2. Client Output (Ruby)

```text
--- RUBY CLIENT STARTING ---
Target: [https://127.0.0.1.nip.io:9090](https://127.0.0.1.nip.io:9090)
Key:    ClientKeyMustBeLongEnough00001

[ACTION] Requesting Token...

[SUCCESS] 🚀 Server Responded!
   > OAuth Token:  sG06Yas6dJeMKPSr15Xa8lPypHTE65
   > OAuth Secret: gMtQB7lvKCuuBYAXhCOqeNYJcqL1My
```
=======
## License
This project is open source and available under the [MIT License](LICENSE).

