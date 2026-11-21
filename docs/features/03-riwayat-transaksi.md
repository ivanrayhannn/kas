# Riwayat Transaksi

Semua catatan uang masuk dan keluar tersusun rapi dan gampang dicari.

## Spesifikasi

### Tujuan
Memberi pemilik satu tempat untuk melihat, mencari, dan memperbaiki semua catatan kas, sehingga salah input bisa ditemukan dan dibetulkan sendiri.

### Selesai bila
- Semua catatan tampil dari yang terbaru, dikelompokkan per tanggal dengan subtotal masuk dan keluar.
- Pencarian dan filter bisa dipakai bersamaan, dan jumlah catatan yang cocok selalu terlihat.
- Setiap perbaikan atau penghapusan langsung mengubah Sisa Kas.

## Sub-fitur: Daftar Semua Transaksi

Lihat seluruh catatan dari yang terbaru sampai terlama.

### Tujuan
Menampilkan seluruh catatan secara berurutan supaya mudah ditelusuri.

### Selesai bila
- Setiap baris menampilkan tanda +/−, kategori, catatan, nominal berwarna (hijau masuk, bata keluar), dan label asal bila otomatis (QRIS, Belanja).
- Daftar dimuat 50 catatan per halaman dengan tombol "Tampilkan lebih banyak".
- Bila belum ada catatan, tampil pesan kosong dengan tombol "Catat transaksi".

## Sub-fitur: Cari & Filter

Temukan catatan tertentu berdasarkan tanggal, jenis, atau kategori.

### Tujuan
Membantu pemilik menemukan satu catatan dengan cepat tanpa menggulir panjang.

### Selesai bila
- Pencarian teks mencocokkan isi catatan dan nama kategori.
- Filter jenis: Semua, Uang Masuk, Uang Keluar.
- Filter periode: Semua, Hari ini, 7 hari, Bulan ini, Pilih tanggal (dari dan sampai).
- Filter kategori menyesuaikan dengan jenis yang dipilih.
- Bila hasil kosong karena filter, tampil tombol "Hapus semua filter".

## Sub-fitur: Detail & Perbaiki

Buka satu catatan untuk melihat rincian atau memperbaiki salah input.

### Tujuan
Membetulkan salah input tanpa harus menghapus dan mencatat ulang.

### Selesai bila
- Detail menampilkan jenis, nominal, kategori, tanggal, catatan, asal, waktu dicatat, dan waktu terakhir diperbaiki.
- Catatan manual bisa diperbaiki (semua isian) dan dihapus, dengan konfirmasi sebelum menghapus.
- Catatan otomatis (dari QRIS atau belanja) tidak bisa diubah, hanya dihapus. Menghapusnya mengembalikan sumbernya: pembayaran kembali ke status Menunggu, daftar belanja kembali bisa diubah.
