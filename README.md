# PrasMenjawab — Gemini FastAPI Boilerplate

Chatbot pribadi **PrasMenjawab**: API FastAPI yang menerima input teks dari user, mengirimnya ke Gemini API, dan mengembalikan jawabannya.

Proyek ini adalah fondasi (Minggu 1-2) untuk proyek besar **"Smart Document AI Assistant"**.

## Fitur

- `POST /api/chat` — kirim `{"prompt": "...", "session_id": "..."}` → dapat `{"response": "...", "session_id": "..."}` (non-streaming)
- `POST /api/chat/stream` — jawaban streaming via SSE (Server-Sent Events)
- **Memori percakapan (multi-turn)** — AI ingat pesan-pesan sebelumnya dalam satu sesi (`session_id`)
- Halaman chat sederhana di `http://localhost:8000/`

## Cara pakai

```bash
# 1. Buat virtual environment (disarankan)
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Siapkan API key
copy .env.example .env
# lalu isi GEMINI_API_KEY dengan key kamu dari https://aistudio.google.com/apikey

# 4. Jalankan server
uvicorn main:app --reload
```

> **Catatan:** setelah mengubah isi `.env`, server perlu di-restart (`Ctrl+C`, lalu jalankan `uvicorn` lagi). Mode `--reload` hanya memantau file `.py`, bukan `.env`.

Buka `http://localhost:8000/` di browser. Dokumentasi API interaktif: `http://localhost:8000/docs`.

## Konfigurasi

Semua lewat file `.env`:

| Variable        | Default              | Keterangan                       |
|-----------------|----------------------|----------------------------------|
| `GEMINI_API_KEY`| (wajib diisi)        | API key dari Google AI Studio    |
| `GEMINI_MODEL`  | `gemini-3.5-flash`   | Nama model Gemini                |
| `AI_NAME`       | `PrasMenjawab`       | Nama/persona AI saat menjawab    |

## Deploy ke Render (gratis)

1. Buat repo di **GitHub** lalu push kode ini (jangan commit `.env` — sudah ada di `.gitignore`).
2. Daftar di **https://render.com** (login via GitHub).
3. Klik **New → Blueprint**, pilih repo kamu. Render akan membaca `render.yaml` dan membuatkan web service otomatis.
4. Saat diminta, isi **Environment Variable** `GEMINI_API_KEY` dengan key kamu dari AI Studio.
5. Tunggu beberapa menit hingga status **Live**, lalu buka URL yang diberikan.

Catatan: paket gratis Render akan "tidur" (sleep) jika tidak dipakai beberapa menit; halaman pertama setelah tidur akan agak lambat (±30 detik).

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
