import os
import io
import re
import json
import uuid
import hashlib
import pypdf
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-001"

FAST_MODEL = "gemini-3.5-flash-lite"
SLOW_MODEL = "gemini-3.5-flash"
REQUESTED_MODEL = os.getenv("GEMINI_MODEL", FAST_MODEL)
MODEL = FAST_MODEL if REQUESTED_MODEL == SLOW_MODEL else REQUESTED_MODEL
FALLBACK_MODEL = SLOW_MODEL if MODEL == FAST_MODEL else FAST_MODEL
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
    return {"version": _ver_value, "model": MODEL, "fallback": FALLBACK_MODEL}


def chunk_text(text: str, max_chars: int = 800, overlap: int = 150) -> list[str]:
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p).strip() if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) > max_chars:
                for i in range(0, len(p), max_chars - overlap):
                    piece = p[i:i + max_chars]
                    if piece.strip():
                        chunks.append(piece.strip())
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    return chunks if chunks else [text] if text else []


class EmbedRequest(BaseModel):
    texts: list[str]


@app.post("/api/embed")
def embed_text(req: EmbedRequest):
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=req.texts,
        )
        embeddings = [e.values for e in result.embeddings]
        return {"embeddings": embeddings}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File harus berformat PDF")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 5 MB")
    reader = pypdf.PdfReader(io.BytesIO(content))
    raw = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            raw += text + "\n\n"
    if not raw.strip():
        raise HTTPException(status_code=400, detail="Tidak ada teks yang bisa dibaca dari PDF ini")
    chunks = chunk_text(raw)
    return {"chunks": chunks, "name": file.filename, "pages": len(reader.pages), "total_chars": len(raw)}


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


def is_quota_error(exc) -> bool:
    return "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc)


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
    contents = build_contents(history, req.prompt)
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
    except Exception as exc:
        if is_quota_error(exc) and MODEL != FALLBACK_MODEL:
            try:
                response = client.models.generate_content(
                    model=FALLBACK_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                    ),
                )
            except Exception as exc2:
                raise HTTPException(status_code=500, detail=str(exc2))
        else:
            raise HTTPException(status_code=500, detail=str(exc))
    text = response.text

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
        used_fallback = False

        def run(model):
            nonlocal full
            stream = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )
            for chunk in stream:
                if chunk.text:
                    full += chunk.text
                    yield f"data: {json.dumps({'delta': chunk.text})}\n\n"

        try:
            yield from run(MODEL)
        except Exception as exc:
            if is_quota_error(exc) and MODEL != FALLBACK_MODEL:
                used_fallback = True
                try:
                    yield from run(FALLBACK_MODEL)
                except Exception as exc2:
                    yield f"data: {json.dumps({'error': str(exc2)})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
            else:
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"
                yield "data: [DONE]\n\n"
                return

        if req.history is None:
            remember(session_id, "user", req.prompt)
            remember(session_id, "model", full)
        yield f"data: {json.dumps({'session_id': session_id, 'model': FALLBACK_MODEL if used_fallback else MODEL})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
