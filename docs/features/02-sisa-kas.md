# Sisa Kas

Lihat berapa uang kas resto yang tersisa saat ini dalam satu layar.

## Spesifikasi

### Tujuan
Menampilkan sisa uang kas resto saat ini dalam satu layar, supaya pemilik langsung tahu kondisi keuangannya tanpa menghitung manual.
### Selesai bila
- Halaman utama menampilkan angka **Sisa Kas** yang besar dan mudah dibaca, dalam format rupiah (mis. Rp 1.250.000).
- Angka sisa kas otomatis berubah dalam beberapa saat setelah ada catatan uang masuk atau uang keluar disimpan, tanpa perlu memuat ulang halaman.
- Terlihat pemisahan singkat antara uang modal dan uang yang sudah terpakai untuk operasional.
- Muncul pemberitahuan yang jelas di layar ini saat kas sudah menipis.
- Bila belum ada catatan sama sekali, tampil angka modal awal dengan keterangan singkat bahwa belum ada transaksi.

## Sub-fitur: Saldo Kas Sekarang

Angka sisa kas yang selalu diperbarui setelah ada catatan baru.

### Tujuan
Menampilkan satu angka sisa kas resto yang selalu akurat dan otomatis diperbarui setiap ada catatan baru.
### Selesai bila
- Angka sisa kas tampil besar di layar utama dengan format rupiah dan pemisah ribuan (mis. Rp 1.250.000).
- Setelah transaksi disimpan, angka sisa kas langsung berubah dan disertai notifikasi singkat "Tersimpan".
- Angka sisa kas dihitung dari modal awal ditambah uang masuk dikurangi uang keluar, dan tidak pernah selisih dengan riwayat transaksi.

## Sub-fitur: Rincian Modal & Operasional

Pisahkan uang modal dengan uang yang sudah terpakai untuk operasional.

### Tujuan
Memisahkan uang modal dari uang yang sudah terpakai untuk operasional agar pemilik tahu seberapa banyak modal yang masih utuh.
### Selesai bila
- Layar menampilkan dua keterangan terpisah: "Modal Awal" dan "Terpakai untuk Operasional", masing-masing dalam format rupiah.
- Nilai "Terpakai untuk Operasional" bertambah otomatis setiap ada catatan uang keluar dan berkurang bila catatan pengeluaran diperbaiki atau dihapus.
- Penjelasan singkat berbahasa sehari-hari tampil di dekat kedua angka sehingga pemilik awam langsung paham artinya.

## Sub-fitur: Peringatan Kas Menipis

Dapatkan pemberitahuan saat kas mulai menipis.

### Tujuan
Memberi tahu pemilik saat sisa kas sudah menipis agar ia segera mengambil tindakan sebelum uang habis.
### Selesai bila
- Muncul peringatan "Kas Menipis" di layar utama saat sisa kas berada di bawah ambang batas yang diatur di Pengaturan Toko.
- Peringatan hilang sendiri saat sisa kas kembali di atas ambang batas.
- Bila ambang batas belum diatur, aplikasi memakai nilai bawaan dan tetap menampilkan peringatan pada waktu yang wajar.
