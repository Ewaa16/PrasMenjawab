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

## Deploy ke Back4app Containers (gratis, tanpa kartu)

Metode: Back4app membangun image dari `Dockerfile`, lalu menjalankan aplikasi di URL
`https://<nama-app>.b4a.run`. Outbound internet bebas, jadi bisa memanggil Gemini API.

> **Kenapa bukan Hugging Face Spaces?** Sejak Juli 2026, akun free baru di HF tidak bisa lagi
> membuat Docker Space (wajib langganan PRO). Back4app Containers masih gratis tanpa kartu.

**Siapkan di laptop (sekali saja):** push kode ke GitHub:

```bash
git add -A
git commit -m "update"
git push -u origin main
```

**Di Back4app (browser):**

1. Daftar di https://www.back4app.com (email + verifikasi, gratis, tanpa kartu).
2. Dari dashboard pilih **Containers** → **Create New App** (Web Deployment).
3. Pilih **Connect GitHub** → Install aplikasi Back4app ke akun GitHub kamu →
   pilih repositori `PrasMenjawab` dan branch `main`.
4. Isi **Environment Variables** (nama harus sama persis seperti di `.env`):
   - `GEMINI_API_KEY` = key kamu dari https://aistudio.google.com/apikey
   - `GEMINI_MODEL` = `gemini-3.5-flash`
   - `AI_NAME` = `PrasMenjawab`
5. Pastikan port container = **8000** (sudah diatur di `Dockerfile`). Klik **Create / Deploy**.
6. Tunggu build selesai, lalu buka URL yang diberikan (bentuknya `https://prasmenjawab-xxxx.b4a.run`).
7. Saat kode berubah: cukup `git push` ke GitHub — Back4app auto-deploy.

> **Catatan:** Back4app memakai port `8000` — sudah diatur di `Dockerfile`.
> Env variable (`GEMINI_API_KEY`) disimpan terenkripsi di dashboard, tidak ikut masuk ke Git.

## Langkah berikutnya (roadmap)

- Minggu 3-4: Membaca PDF + text chunking + embeddings + ChromaDB (RAG)
- Minggu 5-6: Frontend chat ala ChatGPT (React/Next.js) + deploy

## Uji cepat dengan curl

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Halo, siapa kamu?\"}"
```
