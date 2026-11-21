# Pengaturan Toko

Atur identitas resto, QR pembayaran, dan kategori sesuai kebutuhan.

## Spesifikasi

### Tujuan
Menyesuaikan aplikasi dengan resto pemilik tanpa bantuan orang lain.

### Selesai bila
- Semua perubahan tersimpan dengan tombol simpan yang jelas dan diberi konfirmasi singkat.
- Perubahan modal awal dan batas kas menipis langsung berpengaruh ke Sisa Kas dan peringatan.

## Sub-fitur: Profil Toko

Isi nama dan informasi dasar resto yang dipakai di aplikasi.

### Tujuan
Menampilkan identitas resto di aplikasi, di layar QR, dan di laporan.

### Selesai bila
- Nama resto wajib; alamat dan telepon boleh kosong.
- Nama resto tampil di beranda, di layar QR Toko, dan di gambar laporan.

## Sub-fitur: Unggah QR Pembayaran

Pasang gambar QR statis yang akan ditampilkan ke pelanggan.

### Tujuan
Menyimpan foto atau tangkapan layar QRIS statis dari bank atau e-wallet resto.

### Selesai bila
- Pemilik bisa mengunggah, mengganti, dan menghapus gambar QR (PNG, JPG, atau WEBP). Gambar lebih dari sekitar 1 MB diperkecil otomatis sebelum dikirim.
- Pratinjau QR tampil setelah diunggah.

## Sub-fitur: Atur Kategori & Modal Awal

Sesuaikan kategori catatan dan tentukan modal awal resto.

### Tujuan
Menyesuaikan kategori dengan cara resto mencatat, dan menetapkan titik awal sisa kas.

### Selesai bila
- Kategori bisa ditambah dan diganti nama per jenis. Nama kategori tidak boleh kembar dalam satu jenis.
- Kategori yang belum pernah dipakai bisa dihapus; yang sudah dipakai hanya bisa diganti nama, agar riwayat tidak rusak. Setiap jenis minimal punya satu kategori.
- Modal awal bisa diubah kapan saja dan sisa kas dihitung ulang.
- Batas Kas Menipis bisa diisi atau dikosongkan. Bila kosong, dipakai batas bawaan: 20% dari modal awal, minimal Rp 500.000.
