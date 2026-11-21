# Catat Transaksi

Tempat mencatat uang masuk dan uang keluar resto dengan cepat, cukup beberapa ketukan.

## Spesifikasi

### Tujuan
Membuat pemilik resto bisa mencatat setiap penjualan atau pengeluaran saat itu juga, dalam hitungan detik, sehingga tidak ada catatan yang tertunda sampai lupa.

### Selesai bila
- Dari beranda, satu uang masuk atau uang keluar bisa disimpan dengan: tekan Uang Masuk/Uang Keluar, ketik nominal, (pilih kategori bila beda dari terakhir), tekan Simpan.
- Setiap catatan wajib punya jenis, nominal lebih dari 0, kategori, dan tanggal. Catatan teks boleh kosong.
- Tanggal otomatis hari ini dan bisa diubah ke tanggal sebelumnya, tetapi tidak boleh setelah hari ini.
- Setelah tersimpan, layar menampilkan konfirmasi "Tersimpan" beserta sisa kas terbaru.
- Tanpa internet, catatan tetap bisa disimpan di ponsel dan terkirim otomatis saat online.

## Sub-fitur: Catat Uang Masuk

Masukkan penjualan atau uang yang diterima hari ini.

### Tujuan
Mencatat penjualan dan uang yang diterima resto agar langsung menambah sisa kas.

### Selesai bila
- Tombol "+ Uang Masuk" berwarna hijau ada di beranda dan di layar catat.
- Catatan uang masuk yang tersimpan langsung menambah Sisa Kas dan muncul di Riwayat dengan tanda "+".

## Sub-fitur: Catat Uang Keluar

Catat belanja bahan, operasional, dan transportasi yang keluar.

### Tujuan
Mencatat setiap uang yang keluar dari kas resto agar pemilik tahu ke mana uangnya pergi.

### Selesai bila
- Tombol "− Uang Keluar" berwarna bata ada di beranda dan di layar catat.
- Catatan uang keluar langsung mengurangi Sisa Kas, menambah "Terpakai untuk Operasional", dan muncul di Riwayat dengan tanda "−".
- Bila sisa kas turun di bawah batas, muncul peringatan Kas Menipis.

## Sub-fitur: Pilih Kategori Cepat

Pilih kategori yang sudah tersedia agar tidak perlu mengetik panjang.

### Tujuan
Mengelompokkan catatan tanpa mengetik, supaya laporan per kategori bisa dibuat otomatis.

### Selesai bila
- Kategori tampil sebagai tombol besar sesuai jenis (masuk atau keluar), bukan daftar tarik-turun.
- Kategori terakhir yang dipakai per jenis sudah terpilih otomatis saat membuka layar catat.
- Kategori bawaan untuk toko baru: Penjualan, Pembayaran QRIS, Lain-lain (masuk); Bahan Baku, Operasional, Transportasi, Gaji Karyawan, Lain-lain (keluar).

## Sub-fitur: Konfirmasi & Simpan

Periksa nominal lalu simpan, catatan langsung tersimpan tanpa ribet.

### Tujuan
Mencegah salah ketik nominal tanpa menambah langkah konfirmasi yang memperlambat.

### Selesai bila
- Nominal tampil besar dalam format rupiah selama diketik, dan tombol simpan menulis nominalnya ("Simpan Rp 85.000"), jadi pemilik memeriksa sambil menekan.
- Keypad angka besar punya tombol 000 dan tombol hapus satu angka; di komputer, angka bisa diketik dari keyboard.
- Tombol simpan nonaktif selama nominal masih 0.
- Setelah simpan, tersedia pilihan "Catat lagi" dan "Ke beranda".
