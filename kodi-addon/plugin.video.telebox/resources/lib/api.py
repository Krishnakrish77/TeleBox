import xbmcaddon
import requests

addon = xbmcaddon.Addon()
host = addon.getSetting("server_host")
port = addon.getSetting("server_port")

BASE = f"http://{host}:{port}"

def fetch_channels():
    return requests.get(f"{BASE}/channels").json()

def fetch_groups():
    return requests.get(f"{BASE}/groups").json()

def fetch_media(chat_id):
    items = requests.get(f"{BASE}/list/{chat_id}").json()
    for i in items:
        i["stream_url"] = f"{BASE}/stream/{chat_id}/{i['id']}"
    return items
