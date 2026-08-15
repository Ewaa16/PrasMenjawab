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

## Deploy ke Hugging Face Spaces (gratis, tanpa kartu)

Metode: **Docker Space** — HF membangun image dari `Dockerfile`, lalu menjalankan app di
`https://<USERNAME>-prasmenjawab.hf.space`. Outbound internet bebas, jadi bisa memanggil Gemini API.

> **Kenapa bukan PythonAnywhere free?** Paket Free PythonAnywhere memblokir akses internet keluar
> dari web app (`[Errno 101] Network is unreachable`), sehingga chatbot yang memanggil Gemini tidak
> bisa jalan di sana.

**Siapkan di laptop (sekali saja):** push kode ke GitHub:

```bash
git add -A
git commit -m "update"
git push -u origin main
```

**Di Hugging Face (browser):**

1. Daftar di https://huggingface.co/join (email + password, gratis, tanpa kartu).
2. Buat Space: klik avatar → **+ New** → **Space**:
   - Nama: `prasmenjawab`
   - SDK: **Docker**
   - Hardware: **CPU basic** (gratis)
   - Visibility: **Public**
   - Klik **Create Space**.
3. Isi **Variables and secrets** di tab **Settings** Space:
   - `GEMINI_API_KEY` = key kamu dari https://aistudio.google.com/apikey
   - `GEMINI_MODEL` = `gemini-3.5-flash`
   - `AI_NAME` = `PrasMenjawab`
4. Buat Access Token: klik avatar → **Settings** → **Access Tokens** → **Create new token** → scope **Write**.
5. Push kode ke repo Space (di terminal laptop):
   ```bash
   git remote add hf https://huggingface.co/spaces/<USERNAME>/prasmenjawab
   git push hf main
   ```
   Saat diminta username: tulis USERNAME HF kamu; saat diminta password: tempel Access Token tadi.
   Kalau repo Space sudah punya commit awal, pakai `git push -f hf main`.
6. Build berjalan otomatis (lihat tab **Builder**). Selesai, buka:
   `https://<USERNAME>-prasmenjawab.hf.space`
7. Saat kode berubah: `git push hf main` lagi — Space rebuild otomatis.

> **Catatan:** HF Spaces memakai port `7860` — sudah diatur di `Dockerfile`.
> Space free ikut "tidur" saat lama tidak dipakai; kunjungan berikutnya butuh beberapa detik (cold start).

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
