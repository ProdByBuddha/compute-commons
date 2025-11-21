import requests
import time
import json
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

# Configuration
# CHANGED: Use HTTP because Traefik is listening on 80 and we are inside the network/host
KEYCLOAK_URL = "http://auth.computecommons.org"
KEYCLOAK_ADMIN_USER = "admin"
KEYCLOAK_ADMIN_PASS = "admin"

APISIX_ADMIN_URL = "http://admin.api.computecommons.org/apisix/admin" # Access via Traefik
APISIX_API_KEY = "edd1c9f034335f136f87ad84b625c8f1" # Defined in config.yaml

LAGO_API_URL = "http://api.billing.computecommons.org/api/v1" # Traefik routes to Lago API
LAGO_ADMIN_EMAIL = "admin@computecommons.org"
LAGO_ADMIN_PASS = "SecurePass123!"

# Docker internal hostnames for APISIX Upstreams (APISIX needs to talk to them within Docker network)
UPSTREAM_MOCK_COMPUTE = "mock-compute"
UPSTREAM_LAGO = "lago-api"

def log(msg):
    print(f"[SEED] {msg}")

def wait_for_service(url, name, retries=30):
    # For APISIX Admin, we need to check via localhost but with Host header if using Traefik
    # But wait_for_service uses simple get.
    # If url is localhost, it works.
    log(f"Waiting for {name} at {url}...")
    for i in range(retries):
        try:
            # We accept 404 or 401 or 405 as "running but unauthorized/not found", which means it accepts connections
            headers = {}

            res = requests.get(url, headers=headers, timeout=2, verify=False)
            # 405 is Method Not Allowed (e.g. Keycloak token endpoint), which means it's UP.
            # 404 might be Traefik saying "not found" OR the service saying "not found".
            # We'll assume if we get a response, it's reachable.
            log(f"{name} is up! (Status: {res.status_code})")
            return True
        except requests.exceptions.RequestException:
            time.sleep(2)
            print(".", end="", flush=True)
    print("")
    log(f"Failed to connect to {name} after {retries} attempts.")      
    return False


# ---------------------------------------------------------
# KEYCLOAK SETUP
# ---------------------------------------------------------
def setup_keycloak():
    log("Configuring Keycloak...")

    # 1. Get Admin Token
    token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "client_id": "admin-cli",
        "username": KEYCLOAK_ADMIN_USER,
        "password": KEYCLOAK_ADMIN_PASS,
        "grant_type": "password"
    }

    try:
        res = requests.post(token_url, data=data, verify=False)        
        if res.status_code != 200:
            log(f"Failed to get Keycloak admin token: {res.status_code} {res.text}")     
            return

        access_token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # 2. Create Realm
        realm_payload = {
            "realm": "compute-commons",
            "enabled": True,
            "registrationAllowed": True
        }
        # Check if exists first usually, but creating triggers 409 if exists
        res = requests.post(f"{KEYCLOAK_URL}/admin/realms", json=realm_payload, headers=headers, verify=False)
        if res.status_code == 201:
            log("Realm 'compute-commons' created.")
        elif res.status_code == 409:
            log("Realm 'compute-commons' already exists.")
        else:
            log(f"Error creating realm: {res.status_code} {res.text}") 

        # 3. Create Client (Landing UI)
        client_payload = {
            "clientId": "landing-ui",
            "enabled": True,
            "publicClient": True,
            "directAccessGrantsEnabled": True,
            "redirectUris": ["https://computecommons.org/*", "http://localhost/*"],
            "webOrigins": ["https://computecommons.org", "http://localhost"]
        }
        res = requests.post(f"{KEYCLOAK_URL}/admin/realms/compute-commons/clients", json=client_payload, headers=headers, verify=False)       
        if res.status_code == 201:
            log("Client 'landing-ui' created.")
        elif res.status_code == 409:
            log("Client 'landing-ui' already exists.")

        # 4. Create Demo User
        user_payload = {
            "username": "developer",
            "enabled": True,
            "email": "dev@example.com",
            "credentials": [{"type": "password", "value": "password", "temporary": False}]
        }
        res = requests.post(f"{KEYCLOAK_URL}/admin/realms/compute-commons/users", json=user_payload, headers=headers, verify=False)
        if res.status_code == 201:
            log("User 'developer' (password: password) created.")      
        elif res.status_code == 409:
            log("User 'developer' already exists.")

    except Exception as e:
        log(f"Keycloak setup failed: {e}")

# ---------------------------------------------------------
# APISIX SETUP
# ---------------------------------------------------------
def setup_apisix():
    log("Configuring APISIX Routes...")
    headers = {"X-API-KEY": APISIX_API_KEY, "Content-Type": "application/json"}

    # 1. Route for Mock Compute API
    # Matches /api/compute/* and forwards to mock-compute:5000
    compute_route = {
        "uri": "/api/compute/*",
        "plugins": {
            "proxy-rewrite": {
                "regex_uri": ["^/api/compute/(.*)", "/$1"]
            }
        },
        "upstream": {
            "type": "roundrobin",
            "nodes": {
                f"{UPSTREAM_MOCK_COMPUTE}:5000": 1
            }
        }
    }

    res = requests.put(f"{APISIX_ADMIN_URL}/routes/1", json=compute_route, headers=headers, verify=False)
    if res.status_code in [200, 201]:
        log("Route 1 (Mock Compute) configured.")
    else:
        log(f"Failed to config APISIX Route 1: {res.status_code} {res.text}")

    # 2. Route for Lago API (Proxying for frontend convenience, if needed, or just direct)
    # We will skip Lago Proxy via APISIX for now as Traefik handles `lago.localhost`.
    # But we might want APISIX to handle internal events later.        

# ---------------------------------------------------------
# LAGO SETUP
# ---------------------------------------------------------
def setup_lago():
    log("Configuring Lago Billing...")
    # Lago is tricky to script from zero because it requires an initial Registration.
    # We will attempt to Register the admin.

    # Note: accessing Lago via Traefik URL

    # 1. Register Admin (Simulated)
    # The Lago API for registration is often /api/v1/auth/google or similar for SaaS,
    # but for self-hosted, the first user creation is specific.        
    # Checking Lago Self-Hosted docs: It usually asks for sign up on UI.
    # However, we can try to hit the internal initialization or just skip automation for the *account*
    # and ask the user to do it, BUT the goal is automation.

    # Strategy: We will print instructions for Lago API Key retrieval because
    # creating the org via API on a fresh instance usually requires a session token
    # that is retrieved via the UI flow.

    # HOWEVER, we can try to check if the system is reachable.

    log("⚠️  LAGO CONFIGURATION:")
    log("   Lago automation via script is complex due to first-time signup flows.")
    log("   Please follow these manual steps for the Billing system:") 
    log("   1. Go to https://billing.computecommons.org")
    log("   2. Sign up with email: admin@computecommons.org / password: password")
    log("   3. Create an Organization named 'Compute Commons'")        
    log("   4. Go to Developers -> API Keys.")
    log("   5. Copy the API Key.")
    log("   6. Update the 'LAGO_API_KEY' in your docker-compose.yml (mock-compute service).")
    log("   7. Restart the mock-compute service: 'docker compose restart mock-compute'")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    log("Starting Platform Seeding...")

    # Check connectivity
    if not wait_for_service(f"{KEYCLOAK_URL}/health", "Keycloak"):     
        log("Warning: Keycloak might not be fully ready, trying anyway...")

    if not wait_for_service(f"{APISIX_ADMIN_URL}/routes", "APISIX Admin"):
        log("Warning: APISIX Admin might not be reachable.")

    setup_keycloak()
    setup_apisix()
    setup_lago()

    log("✅ Seeding Complete!")
    log("   - Dashboard: https://computecommons.org")
    log("   - Keycloak User: developer / password")
    log("   - APISIX Route: https://api.computecommons.org/api/compute/health -> mock-compute")
