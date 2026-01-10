# TeleBox - Telegram streaming Kodi addon
# Single-file implementation (Baivaru-style)
# Compatible with Kodi Matrix / Nexus / Omega

import sys
import os
import asyncio
import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# -------------------------------------------------------------------
# ADDON PATHS & SETUP
# -------------------------------------------------------------------

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = ADDON.getAddonInfo("path")
PROFILE_PATH = ADDON.getAddonInfo("profile")

# Ensure profile directory exists
os.makedirs(PROFILE_PATH, exist_ok=True)

# Add bundled libraries (Telethon) to Python path
LIB_PATH = os.path.join(ADDON_PATH, "resources", "lib")
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

# -------------------------------------------------------------------
# TELEGRAM SETUP
# -------------------------------------------------------------------

from telethon import TelegramClient

API_ID = int(ADDON.getSetting("api_id"))
API_HASH = ADDON.getSetting("api_hash")

SESSION_FILE = os.path.join(PROFILE_PATH, "telebox.session")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

def ensure_login():
    """
    Ensures the user is logged into Telegram.
    Prompts for phone number on first run.
    """
    if not os.path.exists(SESSION_FILE):
        dialog = xbmcgui.Dialog()
        phone = dialog.input("Enter Telegram phone (+countrycode):")
        client.start(phone=phone)
        dialog.notification("TeleBox", "Telegram login successful", xbmcgui.NOTIFICATION_INFO, 4000)
    else:
        client.connect()
        if not client.is_user_authorized():
            dialog = xbmcgui.Dialog()
            phone = dialog.input("Session expired. Enter phone:")
            client.start(phone=phone)

# -------------------------------------------------------------------
# TELEGRAM DATA FUNCTIONS
# -------------------------------------------------------------------

async def fetch_channels():
    dialogs = await client.get_dialogs()
    return [d for d in dialogs if d.is_channel]

async def fetch_groups():
    dialogs = await client.get_dialogs()
    return [d for d in dialogs if d.is_group]

# -------------------------------------------------------------------
# KODI UI FUNCTIONS
# -------------------------------------------------------------------

HANDLE = int(sys.argv[1])

def add_dir(label, query):
    """
    Adds a directory item to Kodi UI
    """
    url = sys.argv[0] + "?" + urllib.parse.urlencode(query)
    li = xbmcgui.ListItem(label)
    li.setInfo("video", {"title": label})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

def show_root():
    """
    Root menu
    """
    add_dir("📺 Channels", {"action": "channels"})
    add_dir("👥 Groups", {"action": "groups"})
    xbmcplugin.endOfDirectory(HANDLE)

def show_channels():
    ensure_login()
    channels = asyncio.run(fetch_channels())

    for c in channels:
        li = xbmcgui.ListItem(c.title)
        xbmcplugin.addDirectoryItem(
            HANDLE,
            "",
            li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(HANDLE)

def show_groups():
    ensure_login()
    groups = asyncio.run(fetch_groups())

    for g in groups:
        li = xbmcgui.ListItem(g.title)
        xbmcplugin.addDirectoryItem(
            HANDLE,
            "",
            li,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(HANDLE)

# -------------------------------------------------------------------
# ROUTER
# -------------------------------------------------------------------

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))

    action = params.get("action")

    if action == "channels":
        show_channels()
    elif action == "groups":
        show_groups()
    else:
        show_root()

# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    router(sys.argv[2][1:])
