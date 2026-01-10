import os
import sys
from requests_oauthlib import OAuth1Session
import urllib3

# CONFIGURATION
USE_HTTPS = True  
PORT = 9090
CLIENT_KEY =    "ClientKeyMustBeLongEnough00001" 
CLIENT_SECRET = "ClientSecretMustBeLongEnough01"

# Network & SSL Logic
if USE_HTTPS:
    PROTOCOL = "https"
    HOST = "127.0.0.1.nip.io"
    
    # Ensure environment allows standard SSL
    if 'OAUTHLIB_INSECURE_TRANSPORT' in os.environ:
        del os.environ['OAUTHLIB_INSECURE_TRANSPORT']
        
    # Suppress warnings for self-signed certs
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    VERIFY_SSL = False 
else:
    PROTOCOL = "http"
    HOST = "127.0.0.1"
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    VERIFY_SSL = False

TARGET_URL = f"{PROTOCOL}://{HOST}:{PORT}"

# CLIENT LOGIC
print(f"--- PYTHON CLIENT (FULL FLOW) ---")
print(f"Target: {TARGET_URL}")
print(f"Key:    {CLIENT_KEY}")

try:
    # SETUP SESSION
    oauth = OAuth1Session(CLIENT_KEY, client_secret=CLIENT_SECRET, callback_uri='oob')

    # REQUEST TOKEN
    print("\n[STEP 1] Requesting Temporary Token...")
    
    fetch_response = oauth.fetch_request_token(
        f'{TARGET_URL}/oauth/request_token', 
        verify=VERIFY_SSL
    )
    
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    
    print(f"   > Token:  {resource_owner_key}")
    print(f"   > Secret: {resource_owner_secret}")

    # USER AUTHORIZATION
    print("\n[STEP 2] User Authorization")
    
    # Generate the link the user needs to visit
    authorization_url = oauth.authorization_url(f'{TARGET_URL}/oauth/authorize')
    
    print("   > ---------------------------------------------------------")
    print("   > OPEN THIS URL IN YOUR BROWSER:")
    print(f"   > {authorization_url}")
    print("   > ---------------------------------------------------------")
    print("   (The server will show you a 6-digit PIN code. Enter it below.)")
    
    verifier = input("   > PIN Code: ").strip()

    
    #ACCESS TOKEN
    print("\n[STEP 3] Exchanging for Access Token...")
    
    # Re-initialize the session with the Verifier
    oauth = OAuth1Session(
        CLIENT_KEY,
        client_secret=CLIENT_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )

    # Exchange!
    oauth_tokens = oauth.fetch_access_token(
        f'{TARGET_URL}/oauth/access_token',
        verify=VERIFY_SSL
    )
    
    print("\n[SUCCESS] 🚀 OAuth Flow Complete!")
    print(f"   > FINAL Access Token:  {oauth_tokens.get('oauth_token')}")
    print(f"   > FINAL Access Secret: {oauth_tokens.get('oauth_token_secret')}")

except Exception as e:
    print(f"\n[FAILURE] ❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
         print(f"   > Status: {e.response.status_code}")
         print(f"   > Body:   {e.response.text}")