# TeleBox - Telegram Kodi Addon (Single-file, stable version)
# FIXED: Async issues removed, Telethon sync API used

import os
import sys
import urllib.parse

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

from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError


def safe_int(value, default):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


API_ID = safe_int(ADDON.getSetting("api_id"), 0)
API_HASH = ADDON.getSetting("api_hash")
MAX_MESSAGES = max(1, safe_int(ADDON.getSetting("max_messages"), 50))

SESSION_FILE = os.path.join(PROFILE_PATH, "telebox.session")
CACHE_PATH = os.path.join(PROFILE_PATH, "cache")
os.makedirs(CACHE_PATH, exist_ok=True)

SUPPORTED_FILE_EXTENSIONS = (
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".mp3", ".aac", ".m4a", ".wav", ".flac", ".ogg"
)

client = TelegramClient(SESSION_FILE, API_ID, API_HASH)


def notify(msg):
    xbmcgui.Dialog().notification(
        "TeleBox",
        msg,
        xbmcgui.NOTIFICATION_ERROR,
        4000
    )


def ensure_login():
    if not client.is_connected():
        try:
            client.connect()
        except Exception:
            notify("Telegram connection failed")
            return False

    if client.is_user_authorized():
        return True

    dialog = xbmcgui.Dialog()

    phone = dialog.input(
        "Enter your Telegram phone number (with country code)",
        type=xbmcgui.INPUT_ALPHANUM
    )
    if not phone:
        notify("Login cancelled")
        return False

    try:
        client.send_code_request(phone)
    except Exception:
        notify("Failed to send login code")
        return False

    code = dialog.input(
        "Enter the OTP sent to Telegram",
        type=xbmcgui.INPUT_NUMERIC
    )
    if not code:
        notify("OTP required")
        return False

    try:
        client.sign_in(phone=phone, code=code)
        return True

    except SessionPasswordNeededError:
        for attempt in range(3):
            password = dialog.input(
                "2FA is enabled. Enter your password (attempt {0}/3)".format(attempt + 1),
                option=xbmcgui.ALPHANUM_HIDE_INPUT
            )

            if not password:
                notify("Login cancelled")
                return False

            try:
                client.sign_in(**{"password": password})
                return True
            except PasswordHashInvalidError:
                notify("Incorrect password")
            except Exception:
                notify("Login failed")
                return False

        notify("Too many failed attempts")
        return False
    except Exception:
        notify("Login failed")
        return False

# -------------------------------------------------------------------
# TELEGRAM DATA (SYNC)
# -------------------------------------------------------------------

def get_channels():
    if not ensure_login():
        return []
    try:
        dialogs = client.get_dialogs()
    except Exception:
        notify("Failed to load chats")
        return []
    return [d for d in dialogs if d.is_channel]


def get_groups():
    if not ensure_login():
        return []
    try:
        dialogs = client.get_dialogs()
    except Exception:
        notify("Failed to load chats")
        return []
    return [d for d in dialogs if d.is_group]


def is_supported_media(msg):
    if not msg or not msg.file:
        return False

    if msg.video or msg.audio or msg.voice:
        return True

    if not msg.document:
        return False

    file_name = (msg.file.name or "").lower()
    if file_name.endswith(SUPPORTED_FILE_EXTENSIONS):
        return True

    mime_type = (getattr(msg.file, "mime_type", "") or "").lower()
    return mime_type.startswith("video/") or mime_type.startswith("audio/")


def get_media(chat_id, limit):
    if not ensure_login():
        return []

    media = []
    try:
        for msg in client.iter_messages(chat_id, limit=limit):
            if not is_supported_media(msg):
                continue

            name = msg.file.name if msg.file and msg.file.name else "media_{0}".format(msg.id)
            media.append({"id": msg.id, "name": name})
    except Exception:
        notify("Failed to load chat media")
        return []

    return media


def play_media(chat_id, msg_id):
    if not ensure_login():
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    try:
        message = client.get_messages(chat_id, ids=msg_id)
    except Exception:
        notify("Failed to load media")
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    if not message or not message.file:
        notify("Media not found")
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    file_name = sanitize_file_name(message.file.name, "media_{0}".format(msg_id))
    target_path = os.path.join(CACHE_PATH, "{0}_{1}_{2}".format(chat_id, msg_id, file_name))

    if not os.path.exists(target_path):
        try:
            client.download_media(message, file=target_path)
        except Exception:
            notify("Failed to cache media")
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
            return

    if not os.path.exists(target_path):
        notify("Failed to cache media")
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    list_item = xbmcgui.ListItem(path=target_path)
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)


# -------------------------------------------------------------------
# KODI UI HELPERS
# -------------------------------------------------------------------

HANDLE = int(sys.argv[1])


def sanitize_file_name(file_name, fallback):
    cleaned = (file_name or "").replace("\\", "/").split("/")[-1].strip()
    if not cleaned:
        cleaned = fallback
    return "".join(ch if ch.isalnum() or ch in "._- ()" else "_" for ch in cleaned)


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
    for channel in get_channels():
        add_dir(channel.title, {"action": "media", "chat_id": channel.id})
    xbmcplugin.endOfDirectory(HANDLE)


def show_groups():
    for group in get_groups():
        add_dir(group.title, {"action": "media", "chat_id": group.id})
    xbmcplugin.endOfDirectory(HANDLE)


def show_media(chat_id):
    for item in get_media(chat_id, MAX_MESSAGES):
        url = sys.argv[0] + "?" + urllib.parse.urlencode(
            {"action": "play", "chat_id": chat_id, "msg_id": item["id"]}
        )
        li = xbmcgui.ListItem(item["name"])
        li.setInfo("video", {"title": item["name"]})
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(HANDLE, url, li, isFolder=False)
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
    elif action == "media":
        chat_id = safe_int(params.get("chat_id"), None)
        if chat_id is None:
            notify("Invalid chat id")
            show_root()
            return
        show_media(chat_id)
    elif action == "play":
        chat_id = safe_int(params.get("chat_id"), None)
        msg_id = safe_int(params.get("msg_id"), None)
        if chat_id is None or msg_id is None:
            notify("Invalid playback parameters")
            show_root()
            return
        play_media(chat_id, msg_id)
    else:
        show_root()


# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

if __name__ == "__main__":
    router(sys.argv[2][1:])
