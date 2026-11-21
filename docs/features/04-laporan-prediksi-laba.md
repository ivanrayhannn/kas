# Laporan & Prediksi Laba

Ketahui performa harian dan perkiraan keuntungan resto ke depan.

## Spesifikasi

### Tujuan
Menjawab tiga pertanyaan pemilik tanpa hitung manual: untung atau rugi, uang paling banyak habis di mana, dan kira-kira berapa laba ke depan.

### Selesai bila
- Periode bisa dipilih: Hari ini, 7 hari, Bulan ini, atau rentang tanggal sendiri (maksimal 1 tahun).
- Semua angka dihitung dari catatan transaksi, sehingga selalu sama dengan Riwayat dan Sisa Kas.

## Sub-fitur: Laporan Harian

Ringkasan pemasukan, pengeluaran, dan sisa kas tiap hari.

### Tujuan
Melihat pergerakan kas per hari dalam periode yang dipilih.

### Selesai bila
- Ringkasan periode menampilkan uang masuk, uang keluar, laba atau rugi (masuk dikurangi keluar), sisa kas awal dan akhir periode.
- Untuk periode lebih dari satu hari, tabel harian menampilkan masuk, keluar, dan sisa kas akhir tiap tanggal, dari terbaru.
- Hari tanpa catatan tetap tampil dengan nilai kosong.

## Sub-fitur: Rekap per Kategori

Lihat kategori mana yang paling banyak menghabiskan uang.

### Tujuan
Menunjukkan pos pengeluaran terbesar supaya pemilik tahu mana yang perlu dihemat.

### Selesai bila
- Uang keluar dan uang masuk per kategori diurutkan dari terbesar, lengkap dengan total, jumlah catatan, persentase, dan batang perbandingan.

## Sub-fitur: Prediksi Laba

Perkiraan keuntungan berdasarkan modal dan pola penjualan.

### Tujuan
Memberi gambaran laba ke depan dan kapan modal kembali, dengan bahasa yang jelas bahwa ini perkiraan.

### Selesai bila
- Dasar hitungan: rata-rata laba harian (masuk dikurangi keluar) selama 14 hari terakhir, atau sejak catatan pertama bila belum 14 hari. Hari tanpa catatan dihitung 0.
- Prediksi baru tampil bila ada catatan di minimal 3 tanggal berbeda dalam 14 hari terakhir; sebelum itu tampil keterangan berapa hari lagi yang dibutuhkan.
- Ditampilkan: perkiraan laba 7 hari ke depan, perkiraan laba sampai akhir bulan (laba bulan berjalan ditambah rata-rata dikali sisa hari).
- Bila modal awal lebih dari 0: persentase modal yang sudah kembali (laba sejak awal dibagi modal awal) dan perkiraan jumlah hari sampai modal kembali.

## Sub-fitur: Unduh & Bagikan

Simpan atau bagikan laporan dalam bentuk file.

### Tujuan
Mengirim laporan ke pasangan usaha, investor, atau diri sendiri lewat WhatsApp.

### Selesai bila
- "Bagikan gambar" membuat gambar PNG laporan (nama toko, periode, ringkasan, prediksi, 6 kategori pengeluaran terbesar) dan membuka menu bagikan ponsel; di perangkat tanpa menu bagikan, gambar diunduh.
- "Simpan PDF" membuka jendela cetak dengan tampilan bersih tanpa tombol dan menu.
