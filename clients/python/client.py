import os
import sys
from requests_oauthlib import OAuth1Session
import urllib3

# CONFIGURATION
USE_HTTPS = True  

PORT = 9090
CLIENT_KEY =    "ClientKeyMustBeLongEnough00001" 
CLIENT_SECRET = "ClientSecretMustBeLongEnough01"

# Logic to switch between IP and Domain
if USE_HTTPS:
    PROTOCOL = "https"
    HOST = "127.0.0.1.nip.io" # Use Domain for SSL/Cert matching
    # HOST = "127.0.0.1"
    
    # Clean up environment for strict security
    if 'OAUTHLIB_INSECURE_TRANSPORT' in os.environ:
        del os.environ['OAUTHLIB_INSECURE_TRANSPORT']
        
    # Suppress warnings for self-signed certs (Optional)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    VERIFY_SSL = False # Change to "cert.pem" for strict verification
else:
    PROTOCOL = "http"
    HOST = "127.0.0.1" # Use IP for speed/simplicity
    
    # Allow insecure HTTP for OAuth 1.0
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    VERIFY_SSL = False

TARGET_URL = f"{PROTOCOL}://{HOST}:{PORT}"


# CLIENT LOGIC
print(f"--- CLIENT STARTING ---")
print(f"Mode:   {PROTOCOL.upper()}")
print(f"Target: {TARGET_URL}")
print(f"Key:    {CLIENT_KEY}")

try:
    #  Create Session
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='oob')

    # Request Token
    print("\n[ACTION] Requesting Token...")
    
    # We pass verify=VERIFY_SSL to handle the self-signed certs if needed
    fetch_response = oauth.fetch_request_token(
        f'{TARGET_URL}/oauth/request_token', 
        verify=VERIFY_SSL
    )
    
    # Success!
    print(f"\n[SUCCESS] 🚀 Server Responded:")
    print(f"   > OAuth Token:  {fetch_response.get('oauth_token')}")
    print(f"   > OAuth Secret: {fetch_response.get('oauth_token_secret')}")

except Exception as e:
    print(f"\n[FAILURE] ❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
         print(f"   > Status: {e.response.status_code}")
         print(f"   > Body:   {e.response.text}")