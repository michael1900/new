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
import pickle

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
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)


def get_random_device():
    """Genera informazioni casuali ma realistiche sul dispositivo"""
    devices = [
        {
            "brand": "samsung",
            "model": "SM-G973F",
            "name": "Galaxy S10"
        },
        {
            "brand": "xiaomi",
            "model": "M2102J20SG",
            "name": "Redmi Note 10"
        },
        {
            "brand": "google",
            "model": "Pixel 6",
            "name": "pixel"
        }
    ]
    return random.choice(devices)


def create_session():
    session = requests.Session()
    
    # Lista di User-Agents realistici
    user_agents = [
        "Mozilla/5.0 (Linux; Android 12; SM-G973F Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; M2102J20SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "okhttp/4.11.0"
    ]
    
    session.headers.update({
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-Requested-With": "tv.vavoo.app",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept": "application/json, text/plain, */*"
    })
    
    return session

def get_auth_signature():
    session = create_session()
    device = get_random_device()
    device_id = generate_device_id()
    
    current_time = int(time.time() * 1000)
    
    headers = {
        "content-type": "application/json; charset=utf-8",
    }

    data = {
        "token": "8Us2TfjeOFrzqFFTEjL3E5KfdAWGa5PV3wQe60uK4BmzlkJRMYFu0ufaM_eeDXKS2U04XUuhbDTgGRJrJARUwzDyCcRToXhW5AcDekfFMfwNUjuieeQ1uzeDB9YWyBL2cn5Al3L3gTnF8Vk1t7rPwkBob0swvxA",
        "reason": "player.enter",
        "locale": "de",
        "theme": "dark",
        "metadata": {
            "device": {
                "type": "Handset",
                "brand": device["brand"],
                "model": device["model"],
                "name": device["name"],
                "uniqueId": device_id
            },
            "os": {
                "name": "android",
                "version": str(random.randint(10, 13)),  # Versione Android casuale
                "abis": ["arm64-v8a", "armeabi-v7a", "armeabi"],
                "host": "android-" + str(random.randint(25, 33))  # API level casuale
            },
            "app": {
                "platform": "android",
                "version": "3.0.2",
                "buildId": str(random.randint(280000000, 290000000)),
                "engine": "jsc",
                "signatures": ["09f4e07040149486e541a1cb34000b6e12527265252fa2178dfe2bd1af6b815a"],
                "installer": random.choice(["com.android.vending", "com.android.secex"])
            },
            "version": {
                "package": "tv.vavoo.app",
                "binary": "3.0.2",
                "js": "3.1.4"
            }
        },
        "appFocusTime": random.randint(20000, 50000),
        "playerActive": True,
        "playDuration": 0,
        "devMode": False,
        "hasAddon": True,
        "castConnected": False,
        "package": "tv.vavoo.app",
        "version": "3.1.4",
        "process": "app",
        "firstAppStart": current_time - random.randint(1000000, 5000000),
        "lastAppStart": current_time,
        "ipLocation": "",
        "adblockEnabled": random.choice([True, False]),
        "proxy": {
            "supported": ["ss"],
            "engine": "ss",
            "enabled": False,
            "autoServer": True,
            "id": random.choice(["ca-bhs", "de-fra", "nl-ams"])
        },
        "iap": {
            "supported": False
        }
    }

    try:
        # Aggiungi un delay casuale prima della richiesta
        time.sleep(random.uniform(0.5, 1.5))
        
        response = session.post(
            "https://www.vavoo.tv/api/app/ping",
            json=data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("addonSig")
    except Exception as e:
        print(f"Error getting signature: {e}")
        return None

def get_category(channel_name):
    lower_name = channel_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lower_name for keyword in keywords):
            return category
    return "ALTRI"

def setup_logging():
    logging.basicConfig(filename="excluded_channels.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def sanitize_tvg_id(channel_name):
    channel_name = re.sub(r"\.[cs]$", "", channel_name, flags=re.IGNORECASE).strip()
    return " ".join(word.capitalize() for word in channel_name.split())

CHANNEL_FILTERS = [
    "sky", "fox", "rai", "cine34", "real time", "crime+ investigation", "top crime", "wwe", "tennis", "k2",
    "inter", "rsi", "la 7", "la7", "la 7d", "la7d", "27 twentyseven", "premium crime", "comedy central", "super!",
    "animal planet", "hgtv", "avengers grimm channel", "catfish", "rakuten", "nickelodeon", "cartoonito", "nick jr",
    "history", "nat geo", "tv8", "canale 5", "italia", "mediaset", "rete 4",
    "focus", "iris", "discovery", "dazn", "cine 34", "la 5", "giallo", "dmax", "cielo", "eurosport", "disney+", "food", "tv 8", "MOTORTREND",
    "BOING", "FRISBEE", "DEEJAY TV", "CARTOON NETWORK", "TG COM 24", "WARNER TV", "BOING PLUS", "27 TWENTY SEVEN", "TGCOM 24", "SKY UNO", "sky uno"
]

CATEGORY_KEYWORDS = {
    "SKY": ["sky cin", "tv 8", "fox", "comedy central", "animal planet", "nat geo", "tv8", "sky atl", "sky uno", "sky prima", "sky serie"],
    "RAI": ["rai"],
    "MEDIASET": ["mediaset", "canale 5", "rete 4", "italia", "focus"],
    "DISCOVERY": ["discovery", "real time", "investigation", "top crime", "wwe", "hgtv", "nove"],
    "SPORT": ["sport", "dazn", "tennis", "moto", "f1", "golf"],
    "ALTRI": []
}


def get_channel_list(signature, group="Italy"):
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": "MediaHubMX/2",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "mediahubmx-signature": signature
    }

    cursor = 0
    all_items = []

    while True:
        data = {
            "language": "de",
            "region": "AT",
            "catalogId": "vto-iptv",
            "id": "vto-iptv",
            "adult": False,
            "search": "",
            "sort": "name",
            "filter": {"group": group},
            "cursor": cursor,
            "clientVersion": "3.0.2"
        }

        try:
            response = requests.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

            items = result.get("items", [])
            if not items:
                break  # Se non ci sono più canali, esce dal cicloc

            all_items.extend(items)
            cursor += len(items)  # Aggiorna il cursore con il numero di canali ricevuti

        except Exception as e:
            print(f"Errore durante il recupero della lista dei canali: {e}")
            break

    return {"items": all_items}


def resolve_link(link, signature, session, cache):
    if "localhost" in link:
        return link
        
    if link in cache:
        return cache[link]

    # Aggiunge variabilità ai headers per ogni richiesta
    headers = {
        "content-type": "application/json; charset=utf-8",
        "accept": "application/json",
        "mediahubmx-signature": signature,
        "X-Request-ID": ''.join(random.choices('0123456789abcdef', k=32)),
        "X-Client-Version": "3.0.2",
        "X-Platform": "android"
    }

    data = {
        "language": random.choice(["de", "en", "it"]),
        "region": random.choice(["DE", "AT", "CH", "IT"]),
        "url": link,
        "clientVersion": "3.0.2"
    }

    try:
        # Aggiunge un delay casuale naturale
        time.sleep(random.uniform(0.2, 0.7))
        
        response = session.post(
            "https://vavoo.to/vto-cluster/mediahubmx-resolve.json",
            json=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result and "url" in result[0]:
                resolved_url = result[0]["url"]
                cache[link] = resolved_url
                return resolved_url
                
    except requests.exceptions.RequestException:
        pass
    
    return None

def get_channel_list(signature, session, group="Italy"):
    headers = {
        "Accept-Encoding": "gzip",
        "User-Agent": "MediaHubMX/2",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "mediahubmx-signature": signature
    }

    cursor = 0
    all_items = []

    while True:
        data = {
            "language": "de",
            "region": "AT",
            "catalogId": "vto-iptv",
            "id": "vto-iptv",
            "adult": False,
            "search": "",
            "sort": "name",
            "filter": {"group": group},
            "cursor": cursor,
            "clientVersion": "3.0.2"
        }

        try:
            response = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", 
                                  json=data, 
                                  headers=headers,
                                  timeout=10)
            response.raise_for_status()
            result = response.json()

            items = result.get("items", [])
            if not items:
                break

            all_items.extend(items)
            cursor += len(items)
            
            # Add a small delay between requests
            time.sleep(1)

        except Exception as e:
            print(f"Error getting channel list: {e}")
            break

    return {"items": all_items}

# Rest of your code remains the same, but update the generate_m3u function to use the session:

def load_cache(filename="cache.pkl"):
    """Carica la cache da un file se esiste, altrimenti restituisce un dizionario vuoto."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except Exception:
            return {}  # Se il file è corrotto, ritorna una cache vuota
    return {}

def save_cache(cache, filename="cache.pkl"):
    """Salva la cache su file."""
    with open(filename, "wb") as f:
        pickle.dump(cache, f)


def generate_m3u(channels_json, signature, filename="channels.m3u8"):
    setup_logging()
    session = create_session()
    cache = load_cache()  # Ora questa funzione è definita

    items = channels_json.get("items", [])
    if not items:
        logging.error("No channels available.")
        return

    logging.info(f"Processing {len(items)} channels...")
    successful_channels = 0
    failed_channels = 0

    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for idx, item in enumerate(items, 1):
            try:
                name = item.get("name", "Unknown")
                if not any(filter_word.lower() in name.lower() for filter_word in CHANNEL_FILTERS):
                    continue

                original_link = item.get("url")
                if not original_link:
                    continue

                print(f"Channel {idx}/{len(items)}: {name}", end='\r')
                resolved_url = resolve_link(original_link, signature, session, cache)

                if not resolved_url:
                    failed_channels += 1
                    continue

                category = get_category(name)
                tvg_id = sanitize_tvg_id(name)

                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" group-title="{category}",{name}\n')
                f.write('#EXTVLCOPT:http-user-agent=okhttp/4.11.0\n')
                f.write('#EXTVLCOPT:http-origin=https://vavoo.to/\n')
                f.write('#EXTVLCOPT:http-referrer=https://vavoo.to/\n')
                f.write(f'{resolved_url}\n')
                successful_channels += 1

            except Exception as e:
                failed_channels += 1
                continue

    save_cache(cache)  # Salva la cache aggiornata alla fine
    print(f"\nCompleted: {successful_channels} successful, {failed_channels} failed")


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
