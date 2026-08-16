import os
import json
import uuid
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
AI_NAME = os.getenv("AI_NAME", "PrasMenjawab")
MAX_HISTORY = 20
SYSTEM_INSTRUCTION = (
    f"Kamu adalah {AI_NAME}, asisten AI yang ramah dan membantu. "
    "Jawablah dengan jelas dan dalam Bahasa Indonesia."
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY belum di-set. Salin .env.example menjadi .env dan isi API key kamu."
    )

client = genai.Client(api_key=API_KEY)

app = FastAPI(title=f"{AI_NAME} - Chat Assistant")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

SESSIONS: dict[str, list[dict]] = {}

SITE_FILES = [
    BASE_DIR / "static" / "index.html",
    BASE_DIR / "static" / "logo.jpg",
    BASE_DIR / "static" / "bg.jpg",
]
_ver_key = None
_ver_value = None


@app.get("/api/version")
def site_version():
    global _ver_key, _ver_value
    key = tuple(f.stat().st_mtime_ns for f in SITE_FILES)
    if key != _ver_key:
        h = hashlib.sha256()
        for f in SITE_FILES:
            with f.open("rb") as fh:
                h.update(fh.read())
        _ver_key = key
        _ver_value = h.hexdigest()
    return {"version": _ver_value}


class ChatRequest(BaseModel):
    prompt: str
    session_id: str | None = None
    history: list[dict] | None = None


def get_session(req: ChatRequest):
    session_id = req.session_id
    if not session_id or session_id not in SESSIONS:
        session_id = uuid.uuid4().hex
        SESSIONS[session_id] = []
    history = SESSIONS[session_id][-MAX_HISTORY:]
    return session_id, history


def build_contents(history, prompt):
    contents = [
        {"role": msg["role"], "parts": [{"text": msg["text"]}]}
        for msg in history
    ]
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    return contents


def remember(session_id, role, text):
    SESSIONS[session_id].append({"role": role, "text": text})
    if len(SESSIONS[session_id]) > MAX_HISTORY * 2:
        SESSIONS[session_id] = SESSIONS[session_id][-MAX_HISTORY:]


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/chat")
def chat(req: ChatRequest):
    if req.history is not None:
        session_id = None
        history = req.history[-MAX_HISTORY * 2:]
    else:
        session_id, history = get_session(req)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents(history, req.prompt),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        text = response.text
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if req.history is None:
        remember(session_id, "user", req.prompt)
        remember(session_id, "model", text)
    return {"response": text, "session_id": session_id}


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    if req.history is not None:
        session_id = None
        history = req.history[-MAX_HISTORY * 2:]
    else:
        session_id, history = get_session(req)
    contents = build_contents(history, req.prompt)

    def generate():
        full = ""
        try:
            stream = client.models.generate_content_stream(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )
            for chunk in stream:
                if chunk.text:
                    full += chunk.text
                    yield f"data: {json.dumps({'delta': chunk.text})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
            yield "data: [DONE]\n\n"
            return

        if req.history is None:
            remember(session_id, "user", req.prompt)
            remember(session_id, "model", full)
        yield f"data: {json.dumps({'session_id': session_id})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
