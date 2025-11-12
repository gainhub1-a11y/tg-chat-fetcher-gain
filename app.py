import os
import tempfile
import mimetypes
from fastapi import FastAPI, HTTPException, Response, Query, Header
from telethon import TelegramClient
from telethon.sessions import StringSession

# === Environment variables (Render → Environment) ===
# API_ID, API_HASH, STRING_SESSION obbligatori; API_KEY opzionale per proteggere l’API
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
STRING_SESSION = os.environ["STRING_SESSION"]
API_KEY = os.environ.get("API_KEY")  # opzionale

app = FastAPI(title="TG Chat Fetcher (MTProto)", version="1.3.0")
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@app.on_event("startup")
async def startup():
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Telethon session not authorized. Regenerate STRING_SESSION.")

def _name_mime(path: str):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    name = os.path.basename(path) or "file.bin"
    return name, mime

def _coerce_chat_id(v: str | None):
    if not v:
        return None
    s = v.strip()
    if s.startswith("@"):
        return s
    if s.lstrip("-").isdigit():
        try:
            return int(s)
        except Exception:
            pass
    return s

@app.get("/health")
async def health():
    me = await client.get_me()
    return {"ok": True, "user": me.username or me.first_name or me.id}

@app.get("/resolve")
async def resolve(chat_id: str | None = Query(None), peer: str | None = Query(None)):
    try:
        target = peer or _coerce_chat_id(chat_id)
        if not target:
            raise HTTPException(400, "Specify chat_id or peer")
        entity = await client.get_entity(target)
        return {
            "ok": True,
            "title": getattr(entity, "title", None),
            "id": getattr(entity, "id", None),
            "username": getattr(entity, "username", None),
            "class": entity.__class__.__name__,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Resolve error: {e}")

@app.get("/download")
async def download(
    chat_id: str | None = Query(None, description="For channels/groups: -100..., or @username"),
    message_id: int = Query(..., description="Telegram message id containing media"),
    peer: str | None = Query(None, description="For private chats: @BotUsername (or @username della chat)"),
    x_api_key: str | None = Header(default=None, convert_underscores=False),
):
    # Protezione opzionale
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(401, "Unauthorized")

    try:
        # 1) Scegli il target: chat privata (peer) oppure canale/gruppo (chat_id)
        target = peer or _coerce_chat_id(chat_id)
        if not target:
            raise HTTPException(400, "Provide either 'peer' (private) or 'chat_id' (channel/group)")

        entity = await client.get_entity(target)

        # 2) Recupera messaggio
        msg = await client.get_messages(entity, ids=message_id)
        if not msg or not msg.media:
            raise HTTPException(404, "Media not found in that message")

        # 3) Scarica su file temporaneo
        tmpdir = tempfile.mkdtemp()
        path = await client.download_media(msg, file=tmpdir)
        if not path:
            raise HTTPException(500, "Unable to download media")

        # 4) Restituisci binario
        name, mime = _name_mime(path)
        with open(path, "rb") as f:
            data = f.read()
        return Response(
            content=data,
            media_type=mime,
            headers={"Content-Disposition": f'attachment; filename="%s"' % name},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Download error: {e}")

# Avvio locale (facoltativo)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
