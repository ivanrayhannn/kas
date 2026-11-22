# Kas Resto

Aplikasi kas untuk satu restoran: catat uang masuk dan keluar dalam beberapa ketukan, lihat sisa kas, laporan, prediksi laba, pembayaran QRIS dengan verifikasi manual, dan catatan belanja. PWA berbahasa Indonesia, nyaman di ponsel.

Dokumen kebutuhan: [`docs/PRD.md`](docs/PRD.md) dan spesifikasi per fitur di [`docs/features/`](docs/features/). Keputusan yang berbeda dari rencana awal ada di PRD bagian 8.

## Susunan

```
server/   API FastAPI: aturan bisnis, hitung sisa kas, laporan, prediksi (Python)
api/      titik masuk serverless Vercel untuk server/
web/      PWA Vue 3 + Vite + TypeScript + Tailwind + Pinia
tests/    tes aturan bisnis API (pytest)
docs/     PRD dan spesifikasi fitur
```

## Menjalankan di komputer

Butuh Python 3.11+ dan Node 20+.

```bash
pip install -r requirements-dev.txt
```

```bash
python -m uvicorn server.main:app --reload --port 8000
```

Di terminal lain:

```bash
cd web && npm install && npm run dev
```

Buka http://localhost:5173. Data tersimpan di `kas.db` (SQLite). Di mode pengembangan, halaman Lupa kata sandi menampilkan tautan atur ulang langsung di layar karena belum ada server email.

## Tes

```bash
python -m pytest
```

Mencakup: rumus sisa kas, perbaiki/hapus mengubah saldo, validasi nominal dan tanggal, kas menipis dan batas bawaan, pemisahan data antar toko, QRIS verifikasi dan tolak, catatan otomatis terkunci, belanja jadi pengeluaran, laporan harian dan kategori, prediksi laba, keluar akun dan lupa kata sandi, zona waktu ponsel.

Uji alur lengkap di browser (63 langkah: daftar, catat, riwayat, QRIS, belanja, laporan, pengaturan, lupa sandi, offline, tanpa geser samping di layar 320 dan 390 px). Jalankan API di port 8000 dan `npx vite preview` di `web/` setelah `npm run build`, lalu:

```bash
node e2e/flow.cjs
```

## Variabel lingkungan (produksi)

| Nama | Wajib | Isi |
|---|---|---|
| `APP_ENV` | ya | `production` |
| `SECRET_KEY` | ya | teks acak panjang (minimal 32 karakter) untuk menandatangani sesi |
| `DATABASE_URL` | ya | connection string Postgres, mis. dari Supabase (Project Settings, Database) |
| `APP_URL` | tidak | alamat aplikasi, untuk tautan atur ulang kata sandi |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM` | untuk lupa sandi | server email pengirim tautan atur ulang |

Tabel dibuat otomatis saat API pertama kali berjalan.

## Deploy ke Vercel

Satu proyek Vercel dengan dua *services* (lihat `vercel.json`):

| Service | Folder | Framework | Alamat publik |
|---|---|---|---|
| `web` | `web/` | Vite (PWA statis) | `/` dan semua halaman lain; tautan langsung seperti `/riwayat` diarahkan ke `index.html` |
| `app` | `.` (titik masuk `api/index.py`) | FastAPI | `/api/*`, path diteruskan utuh |

Browser memanggil `/api` di domain yang sama, jadi tidak ada panggilan antar-service di server dan tidak perlu *binding*. Isi variabel lingkungan di atas di dashboard Vercel. SQLite tidak bisa dipakai di Vercel (disknya tidak permanen), jadi `DATABASE_URL` wajib diisi Postgres. `APP_URL` boleh dikosongkan: tautan atur ulang sandi memakai alamat situs yang sedang dibuka.
