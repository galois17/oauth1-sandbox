import uvicorn
import sys
import os
import time
import logging
import traceback
from fastapi import FastAPI, Request, Response
from oauthlib.oauth1 import RequestValidator, WebApplicationServer

# CONFIGURATION
USE_HTTPS = True   # Set to True for Docker/Production behavior
PORT = 9090

# 30-char alphanumeric keys (Required for some oauthlib because it's strict)
# (This can be anything that's between 20 and 30 characters, inclusive). 
# Hardcoded here because this just for testing/education purposes.
CLIENT_KEY =    "ClientKeyMustBeLongEnough00001" 
CLIENT_SECRET = "ClientSecretMustBeLongEnough01"

# Network Binding
HOST_BIND = "0.0.0.0" if USE_HTTPS else "127.0.0.1"

# LIBRARY LOGGING (Force oauthlib to speak up)
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# SOPHISTICATED VALIDATOR
class SophisticatedDebugValidator(RequestValidator):
    def __init__(self, is_ssl):
        self.is_ssl = is_ssl
        # IN-MEMORY STORE: (timestamp, nonce)
        self.used_nonces = set()
        super().__init__()

    @property
    def enforce_ssl(self):
        print(f"[DEBUG] enforce_ssl check: {self.is_ssl}")
        return self.is_ssl

    #FORMAT CHECK (Liberal)
    def check_nonce(self, nonce):
        # We accept ANY format. We rely on logic, not regex.
        print(f"[DEBUG] check_nonce: '{nonce}' -> ALLOWED (Format ignored)")
        return True

    # UNIQUENESS CHECK (Strict)
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        print(f"[DEBUG] validate_timestamp_and_nonce: TS={timestamp} | Nonce={nonce}")
        
        try:
            ts = int(timestamp)
        except (TypeError, ValueError):
            print(f"[SEC] REJECTING: Timestamp '{timestamp}' is not an integer")
            return False

        now = int(time.time())
        
        # Window Check (5 Minutes)
        if abs(now - ts) > 300:
            print(f"[SEC] REJECTING: Timestamp {ts} is too old/future (Server Time: {now})")
            return False

        # Replay Attack Check
        nonce_entry = (ts, nonce)
        if nonce_entry in self.used_nonces:
            print(f"[SEC] REPLAY DETECTED! Nonce '{nonce}' was already used.")
            return False

        # Success
        self.used_nonces.add(nonce_entry)
        self._cleanup_old_nonces(now)
        
        print("[SEC] Timestamp & Nonce Valid. Cached.")
        return True

    def _cleanup_old_nonces(self, now):
        initial_size = len(self.used_nonces)
        for ts, n in list(self.used_nonces):
            if (now - ts) > 350:
                self.used_nonces.remove((ts, n))
        if len(self.used_nonces) < initial_size:
            print(f"[SYSTEM] GC: Cleaned up {initial_size - len(self.used_nonces)} old nonces.")

    #KEY VALIDATION 
    def validate_client_key(self, client_key, request):
        print(f"[DEBUG] validate_client_key: '{client_key}'")
        if client_key == CLIENT_KEY:
            return True
        print(f"[SEC] Unknown Client Key: {client_key}")
        return False

    # TRACING STUBS 
    def get_client_secret(self, client_key, request): 
        print(f"[DEBUG] get_client_secret for: {client_key}")
        return CLIENT_SECRET

    def validate_request_token(self, client_key, client_secret, resource_owner_key, request):
        print("[DEBUG] validate_request_token: Checking signature...")
        return True

    def get_request_token_secret(self, client_key, resource_owner_key, request): 
        return "temp_secret"
    
    def validate_redirect_uri(self, client_key, redirect_uri, request):
        print(f"[DEBUG] validate_redirect_uri: {redirect_uri}")
        return True
        
    def validate_callback(self, client_key, callback, request):
        print(f"[DEBUG] validate_callback: {callback}")
        return True 

    def get_default_redirect_uri(self, *args, **kwargs): return "oob"
    def get_default_realms(self, client_key, request): return []
    def validate_requested_realms(self, client_key, realms, request): return True
    
    def save_request_token(self, token, request): 
        print(f"[DEBUG] save_request_token: {token}")
        
    def save_access_token(self, token, request): pass


# Initialize
app = FastAPI()
validator = SophisticatedDebugValidator(is_ssl=USE_HTTPS)
server = WebApplicationServer(validator)

# SERVER LOGIC
async def create_oauth_request(request: Request):
    """
    Translates FastAPI Request to OAuthLib Request.
    """
    body = (await request.body()).decode("utf-8")
    
    # Capitalize Headers
    headers = {}
    for k, v in request.headers.items():
        if k.lower() == 'authorization':
            headers['Authorization'] = v
        elif k.lower() == 'content-type':
            headers['Content-Type'] = v
        else:
            headers[k] = v

    # Force Protocol
    url = str(request.url)
    if USE_HTTPS and not url.startswith("https"):
        url = url.replace("http:", "https:", 1)
            
    # NUCLEAR DEBUGGING
    print("\n" + "="*50)
    print("      INCOMING REQUEST (NUCLEAR DEBUG)")
    print("="*50)
    print(f"URL (Internal):  {url}")
    print(f"Method:          {request.method}")
    print(f"Headers:         {headers}")
    print(f"Body:            '{body}'")
    print("="*50 + "\n")

    return url, request.method, body, headers

@app.post("/oauth/request_token")
async def request_token(request: Request):
    uri, method, body, headers = await create_oauth_request(request)
    
    try:
        h, b, s = server.create_request_token_response(uri, method, body, headers)
        return Response(content=b, status_code=s, headers=h)
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Exception inside OAuthLib: {e}")
        traceback.print_exc()
        return Response(content=str(e), status_code=500)


#STARTUP
if __name__ == "__main__":
    print(f"[SYSTEM] Starting NUCLEAR DEBUG Server on {HOST_BIND}:{PORT}...")
    
    if USE_HTTPS:
        # PATH LOGIC: Check Docker first, then local
        paths = [
            ("/app/certs/key.pem", "/app/certs/cert.pem"), # Docker
            ("key.pem", "cert.pem")                        # Local
        ]
        
        final_key, final_cert = None, None
        
        for k, c in paths:
            if os.path.exists(k) and os.path.exists(c):
                final_key, final_cert = k, c
                print(f"[CERT] Loaded certificates from: {k}")
                break
        
        if not final_key:
            print("[ERROR] HTTPS Enabled but no certificates found!")
            sys.exit(1)
            
        uvicorn.run(app, host=HOST_BIND, port=PORT, log_level="info", 
                    ssl_keyfile=final_key, ssl_certfile=final_cert)
    else:
        uvicorn.run(app, host=HOST_BIND, port=PORT, log_level="info")