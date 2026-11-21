export type Jenis = 'masuk' | 'keluar'

export interface User { id: string; nama: string; email: string }
export interface Store {
  id: string; nama_toko: string; alamat: string | null; telepon: string | null
  modal_awal: number; ambang_kas_menipis: number | null; ambang_efektif: number; ambang_bawaan: boolean
  qr_image: string | null
}
export interface Category { id: string; nama: string; jenis: Jenis; is_default: boolean; dipakai: number }
export interface Transaction {
  id: string; jenis: Jenis; nominal: number; category_id: string; kategori: string; tanggal: string
  catatan: string | null; sumber: 'manual' | 'qris' | 'belanja'; created_at: string; updated_at: string
}
export interface Summary {
  sisa_kas: number; modal_awal: number; total_masuk: number; terpakai_operasional: number
  jumlah_transaksi: number; hari_ini: { tanggal: string; masuk: number; keluar: number }
  ambang_kas_menipis: number; ambang_bawaan: boolean; kas_menipis: boolean; pembayaran_menunggu: number
}
export interface Payment {
  id: string; nominal: number; nama_pelanggan: string | null; status: 'menunggu' | 'terverifikasi' | 'ditolak'
  alasan_tolak: string | null; transaction_id: string | null; created_at: string; verified_at: string | null
}
export interface ShoppingItem {
  id: string; nama_barang: string; jumlah: number; satuan: string | null
  estimasi_harga: number; harga_aktual: number | null; sudah_dibeli: boolean
}
export interface ShoppingList {
  id: string; judul: string; rencana_tanggal: string; status: 'rencana' | 'selesai'
  transaction_id: string | null; jumlah_barang: number; jumlah_dibeli: number
  estimasi_total: number; total_dibeli: number; items?: ShoppingItem[]
}
export interface Prediksi {
  cukup_data: boolean; hari_data?: number; min_hari?: number; dasar_hari?: number; dasar_dari?: string
  rata_rata_laba_harian?: number; perkiraan_7_hari?: number; perkiraan_akhir_bulan?: number
  laba_sejak_awal?: number; persen_balik_modal?: number | null; perkiraan_hari_balik_modal?: number | null
}
export interface KategoriRekap { nama: string; total: number; jumlah: number; persen: number }
export interface Report {
  dari: string; sampai: string; masuk: number; keluar: number; laba: number; jumlah_transaksi: number
  sisa_kas_awal: number; sisa_kas_akhir: number
  harian: { tanggal: string; masuk: number; keluar: number; sisa_kas: number }[]
  kategori_keluar: KategoriRekap[]; kategori_masuk: KategoriRekap[]; prediksi: Prediksi
}
