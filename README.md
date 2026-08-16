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
| `GEMINI_MODEL`  | `gemini-3.5-flash-lite` | Nama model Gemini (lite = paling cepat) |
| `AI_NAME`       | `PrasMenjawab`       | Nama/persona AI saat menjawab    |

## Deploy ke Vercel (gratis, tanpa kartu)

Vercel kini mendukung FastAPI (ASGI) secara native — aplikasi terdeteksi otomatis dari `main.py`,
URL `https://<nama-proyek>.vercel.app`, HTTPS otomatis, dan outbound internet bebas (bisa memanggil Gemini).

> **Kenapa bukan PythonAnywhere / Hugging Face / Back4app?** PAW free memblokir akses internet keluar
> dari web app; HF Spaces sejak Juli 2026 mewajibkan langganan PRO untuk akun free baru; integrasi
> GitHub Back4app rawan gagal menampilkan branch.

**Siapkan di laptop (sekali saja):** push kode ke GitHub:

```bash
git add -A
git commit -m "update"
git push -u origin main
```

**Di Vercel (browser):**

1. Daftar di https://vercel.com → **Continue with GitHub** (pakai akun GitHub kamu).
2. Klik **Add New…** → **Project** → pilih repositori `PrasMenjawab`.
   (Kalau tidak muncul, klik **Adjust GitHub App Permissions** dan izinkan akses ke repo itu.)
3. Vercel otomatis mendeteksi FastAPI — jangan ubah pengaturan build.
4. Isi **Environment Variables** sebelum deploy:
   - `GEMINI_API_KEY` = key kamu dari https://aistudio.google.com/apikey
   - `GEMINI_MODEL` = `gemini-3.5-flash-lite`
   - `AI_NAME` = `PrasMenjawab`
5. Klik **Deploy** → buka URL yang dihasilkan (`https://pras-menjawab.vercel.app`).

> **Catatan:** `.env` tidak ikut ter-commit (aman). Env variable diisi lewat dashboard Vercel.
> Karena app berjalan sebagai serverless function, memori sesi chat hanya bertahan selama instance panas.

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
