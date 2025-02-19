#!/usr/bin/env python3
import requests
import json
import logging
import sys
import re
import time
import os
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def generate_device_id():
    """Genera un ID dispositivo casuale ma coerente"""
    if os.path.exists('.device_id'):
        with open('.device_id', 'r') as f:
            return f.read().strip()
    device_id = ''.join(random.choices('0123456789abcdef', k=16))
    with open('.device_id', 'w') as f:
        f.write(device_id)
    return device_id

def setup_logging():
    """Configure logging settings"""
    logging.basicConfig(
        filename="excluded_channels.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

def get_random_device():
    """Genera informazioni casuali sul dispositivo"""
    devices = [
        {"brand": "samsung", "model": "SM-G973F", "name": "Galaxy S10"},
        {"brand": "xiaomi", "model": "M2102J20SG", "name": "Redmi Note 10"},
        {"brand": "google", "model": "Pixel 6", "name": "pixel"}
    ]
    return random.choice(devices)

def create_session():
    session = requests.Session()
    user_agents = [
        "Mozilla/5.0 (Linux; Android 12; SM-G973F Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; M2102J20SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "okhttp/4.11.0"
    ]
    session.headers.update({
        "User-Agent": random.choice(user_agents),
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-Requested-With": "tv.vavoo.app"
    })
    return session

def get_auth_signature():
    session = create_session()
    device = get_random_device()
    device_id = generate_device_id()
    data = {"token": "<your_token>", "metadata": {"device": {"uniqueId": device_id}}}
    try:
        time.sleep(random.uniform(0.5, 1.5))
        response = session.post("https://www.vavoo.tv/api/app/ping", json=data, timeout=10)
        response.raise_for_status()
        return response.json().get("addonSig")
    except Exception as e:
        print(f"Error getting signature: {e}")
        return None

def get_channel_list(signature, session, group="Italy"):
    headers = {"mediahubmx-signature": signature}
    cursor = 0
    all_items = []
    while True:
        data = {"filter": {"group": group}, "cursor": cursor}
        try:
            response = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=data, headers=headers, timeout=10)
            response.raise_for_status()
            items = response.json().get("items", [])
            if not items:
                break
            all_items.extend(items)
            cursor += len(items)
            time.sleep(1)
        except Exception as e:
            print(f"Error getting channel list: {e}")
            break
    return {"items": all_items}

def resolve_link(link, signature, session):
    if "localhost" in link:
        return link
    headers = {"mediahubmx-signature": signature, "X-Request-ID": ''.join(random.choices('0123456789abcdef', k=32))}
    data = {"url": link}
    try:
        time.sleep(random.uniform(0.2, 0.7))
        response = session.post("https://vavoo.to/vto-cluster/mediahubmx-resolve.json", json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result and "url" in result[0]:
                return result[0]["url"]
    except requests.exceptions.RequestException:
        pass
    return None

def generate_m3u(channels_json, signature, filename="channels.m3u8"):
    setup_logging()
    session = create_session()
    items = channels_json.get("items", [])
    if not items:
        logging.error("No channels available.")
        return
    logging.info(f"Processing {len(items)} channels...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for idx, item in enumerate(items, 1):
            try:
                name = item.get("name", "Unknown")
                original_link = item.get("url")
                if not original_link:
                    continue
                print(f"Channel {idx}/{len(items)}: {name}", end='\r')
                resolved_url = resolve_link(original_link, signature, session)
                if not resolved_url:
                    continue
                f.write(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}", {name}\n{resolved_url}\n')
            except Exception:
                continue
    print("\nCompleted")

def main():
    print("Getting authentication signature...")
    signature = get_auth_signature()
    if not signature:
        print("Failed to get authentication signature.")
        sys.exit(1)
    session = create_session()
    print("Getting channel list...")
    channels_json = get_channel_list(signature, session)
    if not channels_json:
        print("Failed to get channel list.")
        sys.exit(1)
    print("Generating M3U8 file...")
    generate_m3u(channels_json, signature)
    print("Done!")

if __name__ == "__main__":
    main()
