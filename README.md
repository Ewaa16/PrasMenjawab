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

Metode yang dipakai: **ASGI beta** PythonAnywhere — aplikasi FastAPI dijalankan langsung oleh
`uvicorn` (tanpa jembatan WSGI/a2wsgi), jadi streaming & file statis jalan normal.

**Siapkan di laptop (sekali saja):** push kode ke GitHub:

```bash
git add -A
git commit -m "update"
git push -u origin main
```

**Di PythonAnywhere (browser + console):**

1. Daftar di https://www.pythonanywhere.com (paket Free).
2. Buat API token: buka https://www.pythonanywhere.com/account/api_token/ → klik tombol membuat token.
3. Buka tab **Consoles → Bash** (console baru), lalu:
   ```
   git clone https://github.com/Ewaa16/PrasMenjawab.git
   cd PrasMenjawab
   mkvirtualenv --python=python3.12 prasmenjawab
   pip install -r requirements.txt
   ```
4. Buat file `.env` di folder `/home/Ewaa16/PrasMenjawab/` (tab **Files**) berisi:
   ```
   GEMINI_API_KEY=isi_key_kamu
   GEMINI_MODEL=gemini-3.5-flash
   AI_NAME=PrasMenjawab
   ```
5. Install CLI `pa` (di console):
   ```
   pip install --upgrade pythonanywhere
   ```
6. **Hapus web app WSGI lama** di tab **Web** (tombol Delete paling bawah) — domain yang sama dipakai website ASGI.
7. Buat website ASGI (di console):
   ```
   pa website create --domain Ewaa16.pythonanywhere.com --command '/home/Ewaa16/.virtualenvs/prasmenjawab/bin/uvicorn --app-dir /home/Ewaa16/PrasMenjawab --uds ${DOMAIN_SOCKET} main:app'
   ```
8. Saat kode berubah, pull + reload:
   ```
   cd ~/PrasMenjawab && git pull
   pa website reload --domain Ewaa16.pythonanywhere.com
   ```
9. Buka `http://Ewaa16.pythonanywhere.com`.

Log ada di `/var/log/Ewaa16.pythonanywhere.com.{access,error,server}.log`. Paket Free punya batas traffic harian.

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
