import asyncio
from ui import init_telegram_client

LIB_PATH = xbmc.translatePath("special://home/addons/plugin.video.telebox/resources/lib/")
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

client = init_telegram_client()

async def list_channels():
    dialogs = await client.get_dialogs()
    channels = [d for d in dialogs if d.is_channel]
    return [{"id": c.id, "name": c.name} for c in channels]

async def list_groups():
    dialogs = await client.get_dialogs()
    groups = [d for d in dialogs if d.is_group]
    return [{"id": g.id, "name": g.name} for g in groups]

async def list_messages(chat_id, limit=50):
    messages = await client.get_messages(chat_id, limit=limit)
    return [{"id": m.id, "text": m.text, "media": m.media} for m in messages]

def get_channels():
    return asyncio.run(list_channels())

def get_groups():
    return asyncio.run(list_groups())

def get_messages(chat_id, limit=50):
    return asyncio.run(list_messages(chat_id, limit))
