import os
import xbmc
import xbmcgui
from telethon import TelegramClient
from config import API_ID, API_HASH

def init_telegram_client():
    """
    Initializes a TelegramClient for this Kodi user.
    Prompts for phone/OTP on first-time login.
    """
    SESSION_DIR = xbmc.translatePath("special://profile/addon_data/plugin.video.telebox/")
    os.makedirs(SESSION_DIR, exist_ok=True)
    SESSION_FILE = os.path.join(SESSION_DIR, "telebox.session")

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

    # First-time login
    if not os.path.exists(SESSION_FILE):
        dialog = xbmcgui.Dialog()
        phone = dialog.input("Enter your Telegram phone number (+countrycode):")
        client.start(phone=phone)
        dialog.notification("TeleBox", "Telegram login successful!", xbmcgui.NOTIFICATION_INFO, 5000)

    else:
        client.connect()
        if not client.is_user_authorized():
            dialog = xbmcgui.Dialog()
            phone = dialog.input("Session expired! Enter your Telegram phone:")
            client.start(phone=phone)

    return client
