# Pembayaran QRIS

Terima pembayaran pelanggan lewat QR toko, lalu dicatat sebagai pemasukan.

## Spesifikasi

### Tujuan
Memudahkan pemilik resto menerima dan mencatat pembayaran pelanggan lewat QR toko, sehingga uang yang masuk lewat transfer/scan tetap tercatat rapi sebagai pemasukan tanpa perlu hitung manual.

### Selesai bila
- Pemilik bisa menampilkan gambar QR pembayaran tokonya dengan layar yang jelas dan mudah dipindai pelanggan.
- Setiap klaim pembayaran dari pelanggan muncul di daftar "Pembayaran Masuk" dengan status yang jelas (menunggu, terverifikasi, ditolak).
- Pemilik bisa memverifikasi atau menolak klaim pembayaran, dan statusnya langsung berubah.
- Pembayaran yang sudah diverifikasi otomatis tercatat sebagai Uang Masuk dan langsung menambah Sisa Kas.
- Semua teks memakai bahasa Indonesia sehari-hari dan nyaman dipakai di layar ponsel.

## Sub-fitur: Tampilkan QR Toko

Tunjukkan QR pembayaran statis ke pelanggan saat mau bayar.

### Tujuan
Menampilkan gambar QR pembayaran statis milik toko agar pelanggan bisa langsung scan atau transfer saat membayar.

### Selesai bila
- Halaman QR Toko menampilkan gambar QR toko dengan ukuran besar dan jelas di layar ponsel.
- Jika gambar QR belum diunggah, muncul pesan sederhana yang mengarahkan pemilik untuk mengunggahnya di Pengaturan.
- Nama toko tampil di sekitar QR agar pelanggan yakin itu QR resto yang benar.

## Sub-fitur: Daftar Pembayaran Masuk

Pelanggan yang mengaku sudah bayar akan muncul menunggu diperiksa.

### Tujuan
Menampung klaim pembayaran dari pelanggan yang mengaku sudah membayar, supaya pemilik punya daftar untuk diperiksa satu per satu.

### Selesai bila
- Pemilik bisa menambah klaim pembayaran baru dengan nominal dan nama/catatan pelanggan (opsional).
- Daftar "Pembayaran Masuk" menampilkan semua klaim dari yang terbaru, lengkap dengan nominal, nama pelanggan, waktu, dan label status (Menunggu / Terverifikasi / Ditolak).
- Klaim yang masih menunggu ditandai dengan jelas agar mudah dibedakan dari yang sudah selesai.

## Sub-fitur: Verifikasi Manual

Tandai pembayaran sudah benar masuk setelah dicek di rekening.

### Tujuan
Memberi pemilik cara menandai klaim pembayaran sebagai benar masuk setelah dicek di rekening, atau menolaknya bila tidak ditemukan.

### Selesai bila
- Setiap klaim yang menunggu punya tombol jelas "Verifikasi" dan "Tolak".
- Saat menolak, pemilik bisa mengisi alasan penolakan dan alasan itu tampil di detail klaim.
- Setelah diverifikasi atau ditolak, status klaim langsung berubah dan tombol aksinya hilang sesuai status.
- Muncul konfirmasi singkat setelah verifikasi atau penolakan berhasil.

## Sub-fitur: Masuk Otomatis Jadi Pemasukan

Pembayaran yang sudah diverifikasi langsung tercatat sebagai uang masuk.

### Tujuan
Memastikan pembayaran yang sudah diverifikasi langsung tercatat sebagai Uang Masuk tanpa perlu input ulang, sehingga Sisa Kas selalu akurat.

### Selesai bila
- Saat klaim diverifikasi, otomatis terbentuk satu catatan Uang Masuk dengan nominal yang sama dan sumber tertulis dari QRIS.
- Catatan Uang Masuk hasil verifikasi langsung tampil di Riwayat dan menambah Sisa Kas saat itu juga.
- Klaim yang sudah terverifikasi menampilkan penanda bahwa pembayarannya sudah tercatat sebagai pemasukan.
- Klaim yang ditolak tidak mengubah Sisa Kas sama sekali.
