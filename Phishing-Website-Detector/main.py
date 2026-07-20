from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import urllib.parse
import re
import socket
import ssl
import whois
from datetime import datetime
import requests
import warnings

# Suppress insecure request warnings for our intentional redirect checks
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

app = FastAPI(title="PhishGuard API")

# Configure CORS to communicate with the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

# --- Helper Functions for Feature Extraction ---

def is_ip_address(domain: str) -> bool:
    """Check if the domain is actually an IP address."""
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(ip_pattern.match(domain))

def check_ssl_validity(hostname: str) -> bool:
    """Attempt to establish an SSL connection to verify certificate validity."""
    if is_ip_address(hostname):
        return False
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return True
    except Exception:
        return False

def get_domain_age(domain: str) -> int:
    """Perform a WHOIS lookup to calculate the domain age in days."""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            return (datetime.now() - creation_date).days
    except Exception:
        pass
    return 0 # Return 0 if WHOIS fails (often suspicious)

def check_redirects(url: str) -> bool:
    """Send a request to see if the URL masks a redirect chain."""
    try:
        response = requests.get(url, timeout=4, verify=False, allow_redirects=True)
        return len(response.history) > 0
    except requests.RequestException:
        return False

# --- Main API Endpoint ---

@app.post("/api/analyze")
async def analyze_url_endpoint(request: UrlRequest):
    raw_url = request.url
    
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "http://" + raw_url # Default to http for parsing if missing

    try:
        parsed_url = urllib.parse.urlparse(raw_url)
        domain = parsed_url.netloc.split(':')[0] # Strip port if present
        path = parsed_url.path
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed URL structure.")

    # 1. Structural Heuristics
    is_long = len(raw_url) > 75
    has_at_symbol = "@" in raw_url
    has_multiple_hyphens = domain.count("-") > 3
    is_ip = is_ip_address(domain)
    subdomain_count = len(domain.split(".")) - 2 if not is_ip else 0
    subdomain_count = max(0, subdomain_count)
    
    suspicious_tlds = [".xyz", ".top", ".club", ".online", ".zip"]
    suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)

    # 2. Security Features
    has_https = parsed_url.scheme == "https"
    valid_ssl = check_ssl_validity(domain) if has_https else False
    domain_age = get_domain_age(domain)
    has_redirects = check_redirects(raw_url)

    # 3. Scoring Engine (Replace this block with an ML model inference if preferred)
    score = 100
    if not has_https: score -= 20
    if not valid_ssl: score -= 20
    if is_ip: score -= 40
    if has_at_symbol: score -= 30
    if has_multiple_hyphens: score -= 15
    if is_long: score -= 10
    if domain_age > 0 and domain_age < 30: score -= 25 
    if suspicious_tld: score -= 20
    if has_redirects: score -= 15

    score = max(0, min(100, score)) # Clamp between 0 and 100

    if score >= 75:
        verdict = "Safe"
    elif score >= 40:
        verdict = "Suspicious"
    else:
        verdict = "Malicious"

    # Construct and return the exact JSON payload the React frontend expects
    return {
        "url": raw_url,
        "trustScore": score,
        "verdict": verdict,
        "structure": {
            "isLong": is_long,
            "hasAtSymbol": has_at_symbol,
            "hasMultipleHyphens": has_multiple_hyphens,
            "isIpAddress": is_ip,
            "subdomainCount": subdomain_count,
            "suspiciousTld": suspicious_tld
        },
        "security": {
            "hasHttps": has_https,
            "validSsl": valid_ssl,
            "domainAgeDays": domain_age,
            "hasRedirects": has_redirects
        }
    }