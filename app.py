import requests
import json
import time
import os

DNS_API_URL = "http://api.buss.lol/domains"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1242884854052552724/X0JnYD75_0YP47YJq-bvD_ptMMpM4w10fzNtBLMPTXRDyUjg1Y6-O_iEbWgQyCQ1Bujm"
CHECK_INTERVAL = 1
SEEN_DOMAINS_FILE = "seen_domains.json"

def fetch_domains():
    response = requests.get(DNS_API_URL)
    return response.json()

def send_discord_message(embed):
    data = {
        "embeds": [embed]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers=headers)
    if response.status_code != 204:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

def create_embed(domain):
    embed = {
        "title": "New Domain Created!",
        "description": f"Domain: {domain['name']}.{domain['tld']}",
        "color": 0x00ff00,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    return embed

def load_seen_domains():
    if os.path.exists(SEEN_DOMAINS_FILE):
        with open(SEEN_DOMAINS_FILE, "r") as file:
            return set(json.load(file))
    return set()

def save_seen_domains(seen_domains):
    with open(SEEN_DOMAINS_FILE, "w") as file:
        json.dump(list(seen_domains), file)

def monitor_domains():
    seen_domains = fetch_domains()
    seen_domains_set = {f"{domain['name']}.{domain['tld']}" for domain in seen_domains}
    save_seen_domains(seen_domains_set)
    
    while True:
        current_domains = fetch_domains()
        current_domains_set = {f"{domain['name']}.{domain['tld']}" for domain in current_domains}

        new_domains = current_domains_set - seen_domains_set
        seen_domains_set.update(new_domains)
        save_seen_domains(seen_domains_set)

        for domain_name in new_domains:
            for domain in current_domains:
                if f"{domain['name']}.{domain['tld']}" == domain_name:
                    embed = create_embed(domain)
                    send_discord_message(embed)
                    break

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_domains()
