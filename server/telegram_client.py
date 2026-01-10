import os
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from config import API_ID, API_HASH, CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)

client = TelegramClient("telebox", API_ID, API_HASH)

async def start():
    await client.start()

async def stop():
    await client.disconnect();

async def get_channels_and_groups():
    channels, groups = [], []

    async for dialog in client.iter_dialogs():
        entity = dialog.entity

        if isinstance(entity, Channel) and entity.broadcast:
            channels.append({"id": entity.id, "name": entity.title})

        elif isinstance(entity, Chat):
            groups.append({"id": entity.id, "name": entity.title})

    return channels, groups

async def get_videos(chat_id, limit=50):
    videos = []

    async for msg in client.iter_messages(chat_id, limit=limit):
        if msg.video:
            videos.append({
                "id": msg.id,
                "name": msg.file.name or f"video_{msg.id}.mp4"
            })

    return videos

async def download_video(chat_id, msg_id):
    msg = await client.get_messages(chat_id, ids=msg_id)
    path = f"{CACHE_DIR}/{chat_id}_{msg_id}.mp4"

    if not os.path.exists(path):
        await msg.download_media(file=path)

    return path
