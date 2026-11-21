# Masuk & Akun

Amankan data resto dengan akun pribadi yang hanya bisa dibuka pemilik.

## Spesifikasi

### Tujuan
Memastikan data kas hanya bisa dibuka oleh pemilik resto, dari ponsel mana pun.

### Selesai bila
- Satu akun hanya punya satu toko. Semua data (transaksi, kategori, pembayaran, belanja) terkunci ke toko tersebut; akun lain mendapat "tidak ditemukan".
- Semua halaman selain selamat datang, daftar, masuk, dan lupa kata sandi meminta akun.

## Sub-fitur: Daftar Akun

Buat akun baru dengan email dan kata sandi.

### Tujuan
Membuat akun pemilik dalam satu layar, lalu langsung mengisi profil toko.

### Selesai bila
- Pembuka 3 layar singkat tampil sekali di kunjungan pertama, bisa dilewati.
- Daftar meminta nama, email, dan kata sandi minimal 8 karakter. Email yang sudah terdaftar ditolak dengan pesan yang menyarankan masuk.
- Setelah daftar, pemilik mengisi nama resto, modal awal, dan batas kas menipis (boleh kosong), lalu langsung diarahkan ke layar catat transaksi pertama.

## Sub-fitur: Masuk & Keluar

Buka aplikasi dengan akun sendiri dan keluar dengan aman.

### Tujuan
Membuka data kas di perangkat mana pun, dan menutup akses saat ponsel dipinjam atau hilang.

### Selesai bila
- Salah email atau kata sandi menampilkan satu pesan yang sama, tanpa membocorkan mana yang salah.
- Sesi berlaku 30 hari. Saat sesi berakhir, pemilik diarahkan ke halaman masuk dengan pesan yang jelas.
- Keluar mengakhiri sesi di semua perangkat. Bila masih ada catatan offline yang belum terkirim, pemilik diberi tahu sebelum keluar.
- Saat offline, aplikasi tetap terbuka dengan sesi terakhir supaya pemilik bisa mencatat.

## Sub-fitur: Lupa Kata Sandi

Pulihkan akses akun saat lupa kata sandi.

### Tujuan
Membuat kata sandi baru tanpa menghubungi siapa pun.

### Selesai bila
- Pemilik memasukkan email dan menerima tautan atur ulang yang berlaku 1 jam dan hanya bisa dipakai sekali.
- Pesan setelah meminta tautan selalu sama, terdaftar atau tidak, agar orang lain tidak bisa menebak email.
- Setelah kata sandi baru disimpan, semua sesi lama berakhir dan pemilik masuk dengan kata sandi baru.
