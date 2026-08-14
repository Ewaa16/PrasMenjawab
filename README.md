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

## Deploy ke PythonAnywhere (gratis, tanpa kartu)

**Siapkan di laptop (sekali saja):** push kode ke GitHub:

```bash
git add -A
git commit -m "update"
git push -u origin main
```

**Di PythonAnywhere (browser):**

1. Daftar di https://www.pythonanywhere.com (paket Free "Beginner") — pilih username huruf kecil.
2. Buka tab **Consoles → Bash**, lalu ketik:
   ```
   git clone https://github.com/EWaa16/PrasMenjawab.git
   cd PrasMenjawab
   mkvirtualenv --python=python3.12 prasmenjawab
   pip install -r requirements.txt
   ```
3. Buat file `.env` lewat tab **Files** (di folder `/home/<username>/PrasMenjawab/`) berisi:
   ```
   GEMINI_API_KEY=isi_key_kamu
   GEMINI_MODEL=gemini-3.5-flash
   AI_NAME=PrasMenjawab
   ```
4. Tab **Web → Add a new web app → Manual configuration → Python 3.12**.
5. Di halaman pengaturan web app, isi:
   - **Source code:** `/home/<username>/PrasMenjawab`
   - **Working directory:** `/home/<username>/PrasMenjawab`
   - **Virtualenv:** `prasmenjawab`
   - **WSGI configuration file:** arahkan ke `/home/<username>/PrasMenjawab/wsgi.py`
6. Klik **Reload**, lalu buka `http://<username>.pythonanywhere.com`.

Catatan: di PythonAnywhere, streaming (SSE) mungkin tidak mulus — matikan toggle **Streaming** di halaman chat; mode non-streaming dijamin jalan. Paket Free punya batas traffic harian.

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
