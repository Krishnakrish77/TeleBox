# TeleBox - Telegram Kodi Addon (Single-file, stable version)
# FIXED: Async issues removed, Telethon sync API used

import sys
import os
import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# -------------------------------------------------------------------
# ADDON PATHS
# -------------------------------------------------------------------

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = ADDON.getAddonInfo("path")
PROFILE_PATH = ADDON.getAddonInfo("profile")

os.makedirs(PROFILE_PATH, exist_ok=True)

# Add bundled Telethon to path
LIB_PATH = os.path.join(ADDON_PATH, "resources", "lib")
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

# -------------------------------------------------------------------
# TELEGRAM SETUP (SYNC MODE)
# -------------------------------------------------------------------

from telethon.sync  import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = int(ADDON.getSetting("api_id"))
API_HASH = ADDON.getSetting("api_hash")

SESSION_FILE = os.path.join(PROFILE_PATH, "telebox.session")

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

def kodi_input(heading, hidden=False):
    """
    Show a Kodi on-screen keyboard and return user input.
    Returns None if cancelled.
    """
    keyboard = xbmcgui.Dialog()
    result = keyboard.input(
        heading,
        type=xbmcgui.INPUT_ALPHANUM if not hidden else xbmcgui.INPUT_PASSWORD
    )
    return result.strip() if result else None


def ensure_login():
    if client.is_user_authorized():
        return

    phone = kodi_input("Enter your Telegram phone number (with country code)")
    if not phone:
        raise Exception("Phone number required")

    client.send_code_request(phone)

    code = kodi_input("Enter the OTP sent to Telegram")
    if not code:
        raise Exception("OTP required")

    try:
        client.sign_in(phone=phone, code=code)

    except SessionPasswordNeededError:
        password = kodi_input("Enter your Telegram 2-step verification password", hidden=True)
        if not password:
            raise Exception("Password required for 2-step verification")

        client.sign_in(password=password)

# -------------------------------------------------------------------
# TELEGRAM DATA (SYNC)
# -------------------------------------------------------------------

def get_channels():
    ensure_login()
    dialogs = client.get_dialogs()
    return [d for d in dialogs if d.is_channel]

def get_groups():
    ensure_login()
    dialogs = client.get_dialogs()
    return [d for d in dialogs if d.is_group]

# -------------------------------------------------------------------
# KODI UI HELPERS
# -------------------------------------------------------------------

HANDLE = int(sys.argv[1])

def add_dir(label, params):
    url = sys.argv[0] + "?" + urllib.parse.urlencode(params)
    li = xbmcgui.ListItem(label)
    li.setInfo("video", {"title": label})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=True)

# -------------------------------------------------------------------
# SCREENS
# -------------------------------------------------------------------

def show_root():
    add_dir("Channels", {"action": "channels"})
    add_dir("Groups", {"action": "groups"})
    xbmcplugin.endOfDirectory(HANDLE)

def show_channels():
    for c in get_channels():
        li = xbmcgui.ListItem(c.title)
        xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_groups():
    for g in get_groups():
        li = xbmcgui.ListItem(g.title)
        xbmcplugin.addDirectoryItem(HANDLE, "", li, isFolder=False)
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
