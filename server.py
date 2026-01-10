import uvicorn
import sys
import os
import time
import logging
import traceback
import secrets 
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from oauthlib.oauth1 import RequestValidator, WebApplicationServer



# CONFIGURATION
USE_HTTPS = True 
PORT = 9090
CLIENT_KEY = "ClientKeyMustBeLongEnough00001"
CLIENT_SECRET = "ClientSecretMustBeLongEnough01"
HOST_BIND = "0.0.0.0" if USE_HTTPS else "127.0.0.1"

#LOGGING
log = logging.getLogger('oauthlib')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

# Note; oauthlib requires us to do some manual work. oauthlib handles the math, the signatures, the workflow, etc.
# FULL LIFECYCLE VALIDATOR
class SophisticatedDebugValidator(RequestValidator):
    def __init__(self, is_ssl):
        self.is_ssl = is_ssl
        self.used_nonces = set()
        self.tokens = {} 
        super().__init__()

    @property
    def enforce_ssl(self): return self.is_ssl

    # FORMAT CHECKS
    def check_nonce(self, nonce):
        print(f"[DEBUG] check_nonce: '{nonce}' -> ALLOWED")
        return True

    def check_verifier(self, verifier):
        print(f"[DEBUG] check_verifier: '{verifier}' -> ALLOWED")
        return True

    # SECURITY CHECKS
    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, request_token=None, access_token=None):
        try:
            ts = int(timestamp)
        except (TypeError, ValueError): return False
        
        now = int(time.time())
        if abs(now - ts) > 300: return False 
        
        nonce_entry = (ts, nonce)
        if nonce_entry in self.used_nonces:
            print(f"[SEC] REPLAY DETECTED! Nonce {nonce} used twice.")
            return False
        
        self.used_nonces.add(nonce_entry)
        self._cleanup_old_nonces(now)
        return True

    def _cleanup_old_nonces(self, now):
        for ts, n in list(self.used_nonces):
            if (now - ts) > 350: self.used_nonces.remove((ts, n))

    def validate_client_key(self, client_key, request):
        return client_key == CLIENT_KEY

    def get_client_secret(self, client_key, request):
        return CLIENT_SECRET

    # TOKEN LIFECYCLE
    def get_request_token_secret(self, client_key, token, request):
        return self.tokens.get(token, {}).get('secret')

    def save_request_token(self, token, request):
        print(f"[STORE] Saving Request Token: {token}")
        self.tokens[token['oauth_token']] = {
            'secret': token['oauth_token_secret'],
            'authorized': False
        }

    def validate_request_token(self, client_key, token, request):
        return token in self.tokens

    def save_verifier(self, token, verifier, request):
        print(f"[STORE] Saving Verifier {verifier} for Token {token}")
        if token in self.tokens:
            self.tokens[token]['verifier'] = verifier
            self.tokens[token]['authorized'] = True

    def verify_request_token(self, token, request):
        return self.tokens.get(token, {}).get('authorized', False)

    def validate_verifier(self, client_key, token, verifier, request):
        stored = self.tokens.get(token, {}).get('verifier')
        print(f"[DEBUG] Validating Verifier: Client says '{verifier}' vs Stored '{stored}'")
        return stored == verifier

    def save_access_token(self, token, request):
        print(f"[STORE] Issuing Access Token: {token}")
        self.tokens[token['oauth_token']] = {
            'secret': token['oauth_token_secret']
        }

    def get_access_token_secret(self, client_key, token, request):
        return self.tokens.get(token, {}).get('secret')

    def invalidate_request_token(self, client_key, request_token, request):
        print(f"[STORE] Invalidating (Burning) Request Token: {request_token}")
        if request_token in self.tokens:
            del self.tokens[request_token]
    
    # REQUIRED STUBS
    def validate_redirect_uri(self, client_key, redirect_uri, request): return True
    def validate_callback(self, client_key, callback, request): return True 
    def get_default_redirect_uri(self, *args, **kwargs): return "oob"
    def get_default_realms(self, client_key, request): return []
    def validate_requested_realms(self, client_key, realms, request): return True
    def get_realms(self, token, request): return []


app = FastAPI()
validator = SophisticatedDebugValidator(is_ssl=USE_HTTPS)
server = WebApplicationServer(validator)

# HELPER
async def create_oauth_request(request: Request):
    body = (await request.body()).decode("utf-8")
    headers = {}
    for k, v in request.headers.items():
        if k.lower() in ['authorization', 'content-type']:
            headers[k.capitalize()] = v
        else:
            headers[k] = v
            
    url = str(request.url)
    if USE_HTTPS and not url.startswith("https"):
        url = url.replace("http:", "https:", 1)

    print("\n" + "="*50)
    print(f"      INCOMING {request.method} REQUEST")
    print("="*50)
    print(f"URL:     {url}")
    print(f"Headers: {headers}")
    print(f"Body:    {body}")
    print("="*50 + "\n")
    
    return url, request.method, body, headers

# ROUTES
@app.post("/oauth/request_token")
async def request_token(request: Request):
    uri, method, body, headers = await create_oauth_request(request)
    try:
        h, b, s = server.create_request_token_response(uri, method, body, headers)
        return Response(content=b, status_code=s, headers=h)
    except Exception as e:
        print(f"[ERROR] {e}")
        return Response(content=str(e), status_code=400)

@app.get("/oauth/authorize")
async def authorize(request: Request, oauth_token: str):
    # Generate 6-digit number
    verifier = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    
    validator.save_verifier(oauth_token, verifier, request)
    
    return HTMLResponse(content=f"""
    <html>
        <body style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
            <h1>Authorized!</h1>
            <p>Go back to your terminal and enter this code:</p>
            <h2 style='background: #eee; display: inline-block; padding: 10px 20px; font-size: 2em; letter-spacing: 5px;'>{verifier}</h2>
            <p style='color: #888; font-size: 0.9em;'>This code is valid only for token: {oauth_token}</p>
        </body>
    </html>
    """)

@app.post("/oauth/access_token")
async def access_token(request: Request):
    uri, method, body, headers = await create_oauth_request(request)
    try:
        h, b, s = server.create_access_token_response(uri, method, body, headers)
        return Response(content=b, status_code=s, headers=h)
    except Exception as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()
        return Response(content=str(e), status_code=400)


if __name__ == "__main__":
    print(f"[SYSTEM] Starting COMPLETE Server on {HOST_BIND}:{PORT}...")
    
    if USE_HTTPS:
        paths = [("/app/certs/key.pem", "/app/certs/cert.pem"), ("key.pem", "cert.pem")]
        final_key, final_cert = None, None
        for k, c in paths:
            if os.path.exists(k) and os.path.exists(c):
                final_key, final_cert = k, c
                break
        
        if final_key:
            uvicorn.run(app, host=HOST_BIND, port=PORT, ssl_keyfile=final_key, ssl_certfile=final_cert)
        else:
            print("[CRITICAL] No Certs Found. Exiting.")
            sys.exit(1)
    else:
        uvicorn.run(app, host=HOST_BIND, port=PORT)