import ipaddress
import socket
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Blocked private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"), # Cloud metadata endpoints
]

# Blocked exposed file paths
BLOCKED_PATHS = ["/.env", "/.git/config", "/backup.zip", "/wp-config.php", "/.aws/credentials"]

def check_ssrf_and_exposed_files(url: str) -> bool:
    """
    Validates URL to prevent SSRF and access to exposed sensitive files.
    Returns True if safe, raises ValueError if blocked.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    path = parsed.path.lower()
    
    # 1. Check for exposed files
    for blocked_path in BLOCKED_PATHS:
        if blocked_path in path:
            raise ValueError(f"Security Block: Access to exposed sensitive file ({blocked_path}) is prohibited.")
    
    # 2. Resolve DNS and check against private IP ranges
    try:
        # getaddrinfo returns a list of tuples: (family, type, proto, canonname, sockaddr)
        # sockaddr for IPv4 is (ip, port), for IPv6 is (ip, port, flowinfo, scope_id)
        addr_info = socket.getaddrinfo(hostname, None)
        for info in addr_info:
            ip_str = info[4][0]
            ip_addr = ipaddress.ip_address(ip_str)
            
            for network in BLOCKED_NETWORKS:
                if ip_addr in network:
                    raise ValueError(f"Security Block: SSRF prevented. Resolved IP {ip_str} is in a private range.")
                    
            if ip_addr.is_link_local or ip_addr.is_loopback or ip_addr.is_multicast:
                raise ValueError(f"Security Block: SSRF prevented. Resolved IP {ip_str} is unsafe.")
                
    except socket.gaierror:
        raise ValueError(f"Security Block: DNS resolution failed for {hostname}.")
        
    return True