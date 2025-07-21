'''
Extracts context features from a URL or HTML content.
This includes checking for HTTPS, SSL certificate validity, IP address usage,
and presence of sensitive tokens in the URL.
'''

import time
import requests

# This function extracts context features from a given URL.
def get_context_features(url):
    from urllib.parse import urlparse
    import ssl, socket
    import re

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    sensitiveWords = [
        "account", "confirm", "banking", "secure", "ebyisapi", "webscr", "signin", "mail",
        "install", "toolbar", "backup", "paypal", "password", "username", "verify", "update",
        "login", "support", "billing", "transaction", "security", "payment", "online",
        "customer", "service", "accountupdate", "verification", "important", "confidential",
        "limited", "access", "securitycheck", "verifyaccount", "information", "change", "notice",
        "myaccount", "updateinfo", "loginsecure", "protect", "identity", "member",
        "personal", "actionrequired", "loginverify", "validate", "paymentupdate", "urgent", "gcash",
        "auth", "securelogin", "secureaccount", "secureupdate", "secureverify", "secureinfo", "suspended",
        "alert", "warning", "notification", "safety", "securityalert",
        "fraud", "malware", "threat", "compromised", "compromisedaccount", "compromisedinfo", 
        "compromisedsecurity", "compromisedlogin","compromisedupdate", "compromisedverify", 
        "compromisedinfo", "compromisedaccountupdate", "compromisedaccountverify", "compromisedaccountinfo"
    ]

    context = {
        "has_https": url.startswith("https://"),
        "certificate_valid": False,
        "uses_ip_address": bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', hostname)),
        "suspicious_tokens": [word for word in sensitiveWords if word in url.lower()],
        "hostname": hostname
    }

    # SSL cert check 
    if context["has_https"]:
        try:
            conn = ssl.create_default_context().wrap_socket(
                socket.socket(), server_hostname=hostname)
            conn.settimeout(3)
            conn.connect((hostname, 443))
            cert = conn.getpeercert()
            context["certificate_valid"] = True if cert else False
        except:
            context["certificate_valid"] = False

    # Function to check Safe Browsing status with PhishTank (XML response)
    def check_phishtank_xml(url):
        api_url = f"http://checkurl.phishtank.com/checkurl/index.php?url={url}&format=xml"
        headers = {
            "User-Agent": "phishtank/ttm-buoy"
        }
        response = requests.get(api_url, headers=headers)
        raw_content = response.text

        # Check if the response is XML
        if response.headers['Content-Type'] in ("application/xml", "text/xml"):
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(raw_content)
                in_database_element = root.find(".//in_database")
                if in_database_element is not None:
                    return True if in_database_element.text == "true" else False
                else:
                    return False
            except Exception as e:
                return False
        else:
            return False
    
    # Check PhishTank database
    context["phishtank"] = check_phishtank_xml(url)

    def extract_domain(url):
        """Extract domain from URL, removing http/https and paths"""
        url = url.strip()
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Remove www. if present
            domain = re.sub(r'^www\.', '', domain)
            
            return domain
        except:
            return url.split('/')[0].replace('www.', '')

    def check_urlscanio(url, api_key=None, retries=2):
        """
        Check URL against urlscan.io's database
        
        Args:
            url: URL to check (can be with or without http/https)
            api_key: Optional API key
            retries: Number of retries for rate limits
        
        Returns:
            dict: Analysis results
        """
        domain = extract_domain(url)
        headers = {
            "User-Agent": "security-checker/1.0",
            "Accept": "application/json"
        }
        if api_key:
            headers["API-Key"] = api_key

        for attempt in range(retries + 1):
            try:
                # Search by domain only
                search_url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
                response = requests.get(search_url, headers=headers)
                
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 10))
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                search_data = response.json()
                
                if not search_data.get("results"):
                    return {
                        "found": False,
                        "domain": domain,
                        "message": "No existing scans found",
                    }
                
                # Get latest scan
                latest = search_data["results"][0]
                scan_id = latest["task"]["uuid"]
                
                # Get report
                report_url = f"https://urlscan.io/api/v1/result/{scan_id}/"
                report = requests.get(report_url, headers=headers)
                report.raise_for_status()
                report_data = report.json()
                
                verdict = report_data.get("verdicts", {}).get("overall", {})
                
                return {
                    "found": True,
                    "malicious": verdict.get("malicious", False),
                    "phishing": verdict.get("phishing", False),
                    "score": verdict.get("score", 0),
                    "last_scan": latest["task"]["time"],
                }
                
            except requests.exceptions.RequestException as e:
                if attempt == retries:
                    return {
                        "error": str(e),
                        "domain": domain,
                        "status_code": getattr(e.response, 'status_code', None)
                    }
                time.sleep(2 ** attempt) 

    # Check URLScan.io database
    context["urlscan"] = check_urlscanio(url)

    # check for number of redirects
    def check_redirects(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            return len(response.history)
        except requests.RequestException:
            return 0
    
    context["number_of_redirects"] = check_redirects(url)

    return context

#a test example
if __name__ == "__main__":
    url = "http://example.com"
    context = get_context_features(url)
    print(context)