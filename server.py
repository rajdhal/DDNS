import requests
import json

# Update config.json with credentials
def update_data(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

# Obtain current external IP address
def get_current_ip():
    ipaddr = requests.get('https://api.ipify.org').text.strip()
    return ipaddr

# Obtain previous IP from DNS records
def get_previous_ip(api_email, api_key, zone_id, id):
    # GET Request for DNS records https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-dns-record-details
    headers = {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{id}"
    response = requests.get(url, headers=headers)
    o = response.json()
    if response.status_code == 200:
        return o["result"]["content"]
    else:
        return None

# Return Zone ID of domain
def get_zone_id(api_email, api_key, domain_name):
    # Get Zones of Domain https://developers.cloudflare.com/api/operations/zones-get
    headers = {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/"
    response = requests.get(url, headers=headers)
    o=response.json()
    if response.status_code == 200:
        for dict in o["result"]:
            if dict["name"] == domain_name:
                return dict["id"]
    else:
        print("Failed to list Cloudflare DNS records.")
        print("Response:", response.text) 
        return None

# Return list of all domains under account
def get_domains(api_email, api_key) -> list():
    # Get Domains https://developers.cloudflare.com/api/operations/zones-get
    headers = {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/"
    response = requests.get(url, headers=headers)
    o=response.json()
    if response.status_code == 200:
        name_list = []
        for dict in o["result"]:
            name_list.append(dict["name"])
        return name_list
    else:
        print("Failed to list Cloudflare DNS records.")
        print("Response:", response.text) 
        return None

# Return dictionary of all DNS records and IDs
def get_dns_id(api_email, api_key, zone_id) -> dict():
    # List DNS Records https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records
    headers = {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    response = requests.get(url, headers=headers)
    o=response.json()
    # response has a list of dictionaries, keys being id, name, type
    if response.status_code == 200:
        results = {}
        for dict in o["result"]:
            results[dict["name"]] = dict["id"]
        return results
    else:
        print("Failed to list Cloudflare DNS records.")
        print("Response:", response.text)
        return None

# Update the Cloudflare DNS record with the new IP address
def update_dns(api_email, api_key, new_ip, zone_id, record_name, id):
    # Update DNS Record https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record
    headers = {
        "X-Auth-Email": api_email,
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{id}"
    data = {
        "content": new_ip,
        "name": record_name,
        "type": "A"
    }
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Cloudflare DNS record updated successfully.")
    else:
        print("Failed to update Cloudflare DNS record.")
        print("Response:", response.text)  