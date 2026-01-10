# app.py
from fastapi import FastAPI

app = FastAPI()



# Optional: streaming endpoints
@app.get("/stream/{chat_id}/{msg_id}")
async def stream(chat_id: int, msg_id: int):
    # In this multi-user model, streaming can be done via Kodi plugin
    return {"status": "streaming not implemented"}
