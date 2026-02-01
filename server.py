"""Cloudflare API client for DDNS operations."""

import json
import logging
from typing import Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CONFIG_FILE = "config.json"
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
IP_SERVICE_URL = "https://api.ipify.org"
REQUEST_TIMEOUT = 30


class CloudflareAPIError(Exception):
    """Custom exception for Cloudflare API errors."""
    pass


def _build_headers(api_email: str, api_key: str) -> dict:
    """Build authentication headers for Cloudflare API requests."""
    return {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json"
    }


def update_data(data: dict) -> None:
    """Save credentials to config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_config() -> Optional[dict]:
    """Load credentials from config file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_current_ip() -> Optional[str]:
    """Fetch current external IP address from ipify service."""
    try:
        response = requests.get(IP_SERVICE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        logger.error(f"Failed to get current IP: {e}")
        return None


def get_previous_ip(api_email: str, api_key: str, zone_id: str, dns_id: str) -> Optional[str]:
    """Get the current IP address stored in a DNS record."""
    headers = _build_headers(api_email, api_key)
    url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records/{dns_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {}).get("content")
    except requests.RequestException as e:
        logger.error(f"Failed to get DNS record: {e}")
        return None


def get_zone_id(api_email: str, api_key: str, domain_name: str) -> Optional[str]:
    """Get the Zone ID for a domain name."""
    headers = _build_headers(api_email, api_key)
    url = f"{CLOUDFLARE_API_BASE}/zones/"
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        for zone in data.get("result", []):
            if zone.get("name") == domain_name:
                return zone.get("id")
        return None
    except requests.RequestException as e:
        logger.error(f"Failed to get zone ID: {e}")
        return None


def get_domains(api_email: str, api_key: str) -> Optional[list]:
    """Get list of all domain names on the Cloudflare account."""
    headers = _build_headers(api_email, api_key)
    url = f"{CLOUDFLARE_API_BASE}/zones/"
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return [zone.get("name") for zone in data.get("result", [])]
    except requests.RequestException as e:
        logger.error(f"Failed to get domains: {e}")
        return None


def get_dns_records(api_email: str, api_key: str, zone_id: str) -> Optional[dict]:
    """Get dictionary of DNS record names to IDs for a zone."""
    headers = _build_headers(api_email, api_key)
    url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records"
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return {record.get("name"): record.get("id") for record in data.get("result", [])}
    except requests.RequestException as e:
        logger.error(f"Failed to get DNS records: {e}")
        return None


def update_dns(api_email: str, api_key: str, new_ip: str, zone_id: str, 
               record_name: str, dns_id: str) -> bool:
    """Update a DNS A record with a new IP address. Returns True on success."""
    headers = _build_headers(api_email, api_key)
    url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records/{dns_id}"
    payload = {
        "content": new_ip,
        "name": record_name,
        "type": "A"
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.info(f"Updated DNS record {record_name} to {new_ip}")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to update DNS record: {e}")
        return False


# Backwards compatibility alias
get_dns_id = get_dns_records
