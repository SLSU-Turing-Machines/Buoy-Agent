#---------------------------------
# This file contains the functions to tokenize the Website data.
#---------------------------------

import ast
from datetime import datetime
import math
from typing import Counter
import pandas as pd
import re
from urllib.parse import urlparse
from sklearn.feature_extraction.text import CountVectorizer
import ast

def tokenize_url(url):
    try:
        components = urlparse(url)
        return [
            len(components.path),  # Path length
            len(components.query),  # Query length
        ]
    except Exception:
        raise ValueError("URL can't be found or parsed")

# Initialize the vectorizer for domain and TLD
vectorizer = CountVectorizer(analyzer='word', token_pattern=r'\w+')

def tokenize_hostname(hostname):
    """
    Tokenizes the hostname by splitting it into subdomains, domain, and TLD.
    Automatically vectorizes the domain and TLD without the need for predefined lists.
    """
    parts = hostname.split(".")
    
    # Ensure there are exactly 3 tokens: subdomain_count, domain, tld
    subdomain_count = len(parts) - 1 if len(parts) > 1 else 0  # Subdomain count (excluding TLD)
    
    # Extract domain and TLD
    domain_tld = f"{parts[-2]}.{parts[-1]}" if len(parts) > 1 else ""

    # Fit vectorizer on the first pass (you can also fit it on a larger set of data in practice)
    domain_tld_vector = vectorizer.fit_transform([domain_tld]).toarray().flatten()

    # Return a list that contains: subdomain count and the vectorized domain and TLD components
    return [subdomain_count] + domain_tld_vector.tolist()

def doesUrlHaveIP(url):
    """
    Checks if the URL contains an IP address.
    Returns 1 if an IP address is found, 0 otherwise.
    """
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    return 1 if re.search(ip_pattern, url) else 0

def doesUrlHaveHTTPS(url):
    """
    Checks if the URL uses HTTPS.
    Returns 1 if HTTPS is used, 0 if HTTP is used.
    """
    return 1 if url.startswith("https") else 0

def tokenize_certificate(certificate):
    """
    Parses certificate string or dict and returns 1 if the cert is still valid, 0 if expired or invalid.
    """
    if certificate is None:
            return 0

    try:
        if isinstance(certificate, str):
            certificate = ast.literal_eval(certificate)

        if not isinstance(certificate, dict) or "not_after" not in certificate:
            return 0

        expiry_date = pd.to_datetime(certificate["not_after"])
        current_date = datetime.now()
        current_date = pd.to_datetime(current_date, format="%Y%m%d%H%M%SZ")

        return int(expiry_date > current_date)
    
    except Exception as e:
        return 0

def tokenize_html_content(html_content):
    """
    Extracts features from HTML content and returns the counts of various elements.
    """
    # Default output: 6 count features
    default_output = [0] * 6

    # Ensure html_content is a string
    html_content = str(html_content)

    # If it's not a valid string, return the default output
    if not isinstance(html_content, str):
        return default_output

    # Try converting the string to a list
    try:
        data = ast.literal_eval(html_content)
    except (ValueError, SyntaxError):
        print(f"Invalid input format: {html_content}")  # Optional: print invalid input
        return default_output  # Return default output if the format is invalid

    # Extract counts if the data structure is valid
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        try:
            content = ast.literal_eval(data[0])
        except (ValueError, SyntaxError):
            return default_output  # If nested parsing fails, return default

        # Extract actual counts instead of presence flags
        scripts = len(content.get("scripts", []))
        forms = len(content.get("forms", []))
        iframes = len(content.get("iframes", []))
        post_requests = len(content.get("post_requests", []))
        favicons = len(content.get("favicon", []))
        external_resources = len(content.get("external_resources", []))

        # Return the counts instead of binary flags
        return [scripts, forms, iframes, post_requests, favicons, external_resources]

    return default_output  # Return default output if the structure is not as expected

# List of sensitive words commonly found in phishing URLs
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

def sensitive_word(url):
  """
  Checks if the URL contains sensitive words.
  Returns 1 if a sensitive word is found, 0 otherwise.
"""
  for i in sensitiveWords:
    if i in url:
      return 1
  return 0

def url_length(url):
    """
    Returns the length of the URL.
    """
    return len(url)

def url_entropy(url):
    """
    Returns the entropy of the URL. 
    - Entropy is a measure of randomness or unpredictability.
    """
    p, lns = Counter(url), float(len(url))
    return -sum( count/lns * math.log(count/lns, 2) for count in p.values())

def ratio_char_digit(url):
    """
    Returns the ratio of digits to characters in the URL.
    """
    if len(url) == 0:
        return 0
    return round(sum(c.isdigit() for c in url) / len(url), 2)

def tokenize(data):
    """
    Main function to preprocess URL data.
    Ensures that all columns are filled and tokenizes the data.
    """
    # Tokenize features
    data["url_tokens"] = data["final_url"].apply(tokenize_url)
    data["url_length"] = data["final_url"].apply(url_length)
    data["url_entropy"] = data["final_url"].apply(url_entropy)
    data["ratio_char_digit"] = data["final_url"].apply(ratio_char_digit)
    data["sensitive_word"] = data["final_url"].apply(sensitive_word)
    data["hostname_tokens"] = data["hostname"].apply(tokenize_hostname)
    data["has_ip"] = data["final_url"].apply(doesUrlHaveIP)
    data["has_https"] = data["final_url"].apply(doesUrlHaveHTTPS)
    data["certificate_tokens"] = data["certificate"].apply(tokenize_certificate)
    data["html_tokens"] = data["html_content"].apply(tokenize_html_content)

    # Flatten lists
    feature_columns = ["url_tokens", "hostname_tokens", "certificate_tokens", "html_tokens"]
    for col in feature_columns:
        df_expanded = pd.DataFrame(data[col].tolist(), index=data.index)
        df_expanded.columns = [f"{col}_{i}" for i in range(df_expanded.shape[1])]
        data = pd.concat([data, df_expanded], axis=1)
    
    # Drop original list columns
    data.drop(columns=feature_columns, inplace=True)
    return data
