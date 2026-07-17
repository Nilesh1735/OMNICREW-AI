import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def validate_target_url(url: str) -> dict:
    """
    Validates URL scheme, SSL certificate, and HSTS headers.
    Returns a dictionary with validation status and security warnings.
    """
    result = {"is_valid": True, "warnings": [], "errors": []}
    parsed = urlparse(url)
    
    # 1. Enforce HTTPS
    if parsed.scheme != 'https':
        result["is_valid"] = False
        result["errors"].append("Insecure protocol: HTTP is blocked. HTTPS is required.")
        return result
        
    hostname = parsed.hostname
    port = 443
    
    # 2. Check SSL Certificate Expiration
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse expiry date
                expiry_date_str = cert['notAfter']
                expiry_date = datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
                days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days
                if days_until_expiry < 0:
                    result["is_valid"] = False
                    result["errors"].append(f"SSL Certificate expired {-days_until_expiry} days ago.")
                elif days_until_expiry < 30:
                    result["warnings"].append(f"SSL Certificate expires in {days_until_expiry} days.")
    except Exception as e:
        result["is_valid"] = False
        result["errors"].append(f"SSL validation failed: {str(e)}")
        return result

    # 3. Check for HSTS Header (Strict-Transport-Security)
    try:
        # We use a simple socket request to avoid importing requests here
        req = f"HEAD {parsed.path or '/'} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssock.send(req.encode('utf-8'))
                response_data = ssock.recv(4096).decode('utf-8', errors='ignore').lower()
                
        if 'strict-transport-security' not in response_data:
            result["warnings"].append("Missing HSTS header (Strict-Transport-Security).")
    except Exception as e:
        result["warnings"].append(f"Failed to check HSTS headers: {str(e)}")

    return result