const angka = new Intl.NumberFormat('id-ID')

export const rp = (n: number) => `${n < 0 ? '−' : ''}Rp ${angka.format(Math.abs(n))}`
export const rpSigned = (n: number, jenis: 'masuk' | 'keluar') => `${jenis === 'masuk' ? '+' : '−'} ${rp(n)}`

/** Tanggal lokal (Asia/Jakarta di ponsel pemilik) sebagai YYYY-MM-DD. */
export function isoDate(d = new Date()) {
  const p = (x: number) => String(x).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

export function addDays(iso: string, days: number) {
  const d = new Date(`${iso}T00:00:00`)
  d.setDate(d.getDate() + days)
  return isoDate(d)
}

export function tanggalPanjang(iso: string) {
  const today = isoDate()
  if (iso === today) return 'Hari ini'
  if (iso === addDays(today, -1)) return 'Kemarin'
  return new Date(`${iso}T00:00:00`).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

export const tanggalPendek = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })

export const jam = (isoDateTime: string) =>
  new Date(isoDateTime).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })

export const waktu = (isoDateTime: string) =>
  new Date(isoDateTime).toLocaleString('id-ID', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })

/** Ambil angka dari input bebas seperti "Rp 25.000" atau "25000". */
export const parseRupiah = (s: string) => Number(s.replace(/\D/g, '').slice(0, 12) || 0)
