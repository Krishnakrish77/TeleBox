import aiofiles
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from telegram_client import (
    start,
    get_channels_and_groups,
    get_videos,
    download_video
)
from config import CHUNK_SIZE

app = FastAPI()

@app.on_event("startup")
async def startup():
    await start()

@app.get("/channels")
async def channels():
    channels, _ = await get_channels_and_groups()
    return channels

@app.get("/groups")
async def groups():
    _, groups = await get_channels_and_groups()
    return groups

@app.get("/list/{chat_id}")
async def list_media(chat_id: int):
    return await get_videos(chat_id)

@app.get("/stream/{chat_id}/{msg_id}")
async def stream(chat_id: int, msg_id: int):
    path = await download_video(chat_id, msg_id)

    async def iterator():
        async with aiofiles.open(path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    return StreamingResponse(iterator(), media_type="video/mp4")
