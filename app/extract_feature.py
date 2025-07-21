# ------------------------------------------
# This file contains the main synchronous function to fetch web description
#-------------------------------------------

import json
import re
import OpenSSL
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import socket
from datetime import datetime
import ssl
from fake_useragent import UserAgent
import whois

#------------------------------------
# This function fetches the web description of a given URL.
# The function extracts various details such as redirection chain, final URL, hostname, IP address, country, SSL certificate, meta description, HTML content, hosting provider, and abuse contact.
# The function returns a dictionary containing the extracted details.
#------------------------------------
def get_web_desc(url):
    if not url.startswith("http"):
        url = "http://" + url

    result = {
        "redirection_chain": None,
        "final_url": None,
        "hostname": None,
        "ip_address": None,
        "country": None,
        "certificate": None,
        "description": None,
        "html_content": None,

        "hosting_provider": None,
        "abuse_contact": None,
    }

    try:
        # Fetch redirection chain and final URL
        redirection_chain = []
        response = requests.get(url, timeout=10, allow_redirects=True)
            
        for history in response.history:
            redirection_chain.append(str(history.url))  # Convert URL object to string
        redirection_chain.append(str(response.url))  # Convert final URL object to string

        # Set redirection chain to None if there are no redirects
        if len(redirection_chain) == 1:  
            redirection_chain = None 

        result["final_url"] = str(response.url)

        result["redirection_chain"] = redirection_chain

        # Extract hostname and IP address
        parsed_url = urlparse(result["final_url"])
        result["hostname"] = parsed_url.hostname
        result["ip_address"] = socket.gethostbyname(parsed_url.hostname)

        # Extract hosting provider and abuse contact
        try:
            whois_data = whois.whois(result["hostname"])
            result["hosting_provider"] = whois_data.get("org")
            result["abuse_contact"] = whois_data.get("emails")
        except Exception as e:
            result["hosting_provider"] = str(e)
            result["abuse_contact"] = str(e)

        # Extract SSL certificate if HTTPS
        if parsed_url.scheme == "https":
            result["certificate"] = fetch_ssl_certificate(parsed_url.hostname)

        # Extract meta description and HTML content
        page_content = response.text
        soup = BeautifulSoup(page_content, "html.parser")
        meta_desc = soup.find("meta", attrs={"name": "description"})
        result["description"] = meta_desc["content"] if meta_desc else None

        # Extract JavaScript and other suspicious elements
        script_tags = [str(tag) for tag in soup.find_all("script") if tag]
        form_tags = [str(tag) for tag in soup.find_all("form")]
        iframe_tags = [str(tag) for tag in soup.find_all("iframe")]
        post_requests = [str(tag) for tag in soup.find_all("form", attrs={"method": "post"})]
        favicon = [str(tag) for tag in soup.find_all("link", attrs={"rel": "icon"})]

        # Define suspicious patterns using regex
        suspicious_patterns = [
            r"\$.ajax\(",  # AJAX requests (jQuery)
            r"fetch\(",  # Fetch API
            r"new XMLHttpRequest\(",  # XMLHttpRequest object
            r"FormData\(",  # FormData object
            r"cookie",  # Cookie usage
            r"document\.cookie",  # Direct cookie manipulation
            r"window\.postMessage",  # Cross-origin communication via postMessage
            r"eval\(",  # eval usage (dangerous)
            r"localStorage\.",  # localStorage usage
            r"sessionStorage\.",  # sessionStorage usage
            r"indexedDB\.",  # indexedDB usage
            r"openDatabase\(",  # openDatabase usage
        ]

        # Compile all regex patterns at once
        compiled_patterns = [re.compile(pattern) for pattern in suspicious_patterns]

        # To store suspicious script blocks (start and end of function-like blocks)
        suspicious_script_blocks = []

        # Iterate over script tags once and check all patterns
        for script in script_tags:
            for pattern in compiled_patterns:
                # Check for matches with each compiled pattern
                matches = pattern.findall(script)
                for match in matches:
                    # Capture the suspicious block
                    suspicious_script_blocks.append(match.strip())

        # If suspicious_script_blocks is empty set entire script_tag as suspicious
        # limit the character length to 700
        # minify the script_tag by removing unnecessary whitespaces
        if not suspicious_script_blocks:
            script_tags = [re.sub(r"\s+", " ", tag) for tag in script_tags]
            script_tags = [tag[:700] for tag in script_tags]
            suspicious_script_blocks = script_tags

        # Analyze external resources
        external_resources = [link.get("href") for link in soup.find_all("link", href=True)] + \
                             [script.get("src") for script in soup.find_all("script", src=True)]
        html_content = {
            "scripts": suspicious_script_blocks,
            "forms": form_tags,
            "iframes": iframe_tags,
            "post_requests": post_requests,
            "favicon": favicon,
            "external_resources": external_resources,
        }
        result["html_content"] = [json.dumps(html_content)]

    except Exception as e:
        result["error"] = str(e)
    
    # Get geo location
    try:
        # Random User-Agent generator
        ua = UserAgent()
        user_agent = ua.random

        headers = {
            "User-Agent": user_agent
        }
        
        ip_resp = requests.get(f"http://ip-api.com/json/{result['ip_address']}", headers=headers, timeout=10)
        ip_info = ip_resp.json()
        result["country"] = ip_info.get("country")
    except Exception as e:
        result["error"] = str(e)

    # Delete last column if exists
    result.pop("error", None)
    return result

# Function to fetch SSL certificate synchronously
def fetch_ssl_certificate(hostname):
    try:
        context = ssl.create_default_context()
        connection = socket.create_connection((hostname, 443))
        secure_sock = context.wrap_socket(connection, server_hostname=hostname)
        cert_bin = secure_sock.getpeercert(binary_form=True)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_bin)
        cert_details = {
            "issuer": {key.decode(): value.decode() for key, value in x509.get_issuer().get_components()},
            "subject": {key.decode(): value.decode() for key, value in x509.get_subject().get_components()},
            "not_before": datetime.strptime(x509.get_notBefore().decode("ascii"), "%Y%m%d%H%M%SZ").isoformat(),
            "not_after": datetime.strptime(x509.get_notAfter().decode("ascii"), "%Y%m%d%H%M%SZ").isoformat(),
        }
        secure_sock.close()
        return cert_details
    except Exception as e:
        return {"error": str(e)}
