import { rp, tanggalPendek } from './format'
import type { Report } from './types'

/** Gambar laporan sebagai PNG, siap dikirim lewat WhatsApp. Selalu berwarna terang supaya terbaca di mana saja. */
export async function reportPng(r: Report, namaToko: string, judul: string): Promise<Blob> {
  await document.fonts.ready
  const W = 1080, pad = 72, rowH = 64
  const kat = r.kategori_keluar.slice(0, 6)
  const H = 760 + kat.length * rowH + (r.prediksi.cukup_data ? 150 : 0)
  const c = document.createElement('canvas')
  c.width = W
  c.height = H
  const g = c.getContext('2d')!
  const font = (w: number, s: number) => `${w} ${s}px "Plus Jakarta Sans Variable", system-ui, sans-serif`
  const ink = '#1c2620', muted = '#55605a', line = '#e2dccd', masuk = '#1b6943', keluar = '#a33d27'

  g.fillStyle = '#f6f3ea'
  g.fillRect(0, 0, W, H)
  let y = pad + 20
  g.fillStyle = ink
  g.font = font(800, 44)
  g.fillText(namaToko, pad, y)
  y += 48
  g.fillStyle = muted
  g.font = font(500, 30)
  const periode = r.dari === r.sampai ? tanggalPendek(r.dari) : `${tanggalPendek(r.dari)} sampai ${tanggalPendek(r.sampai)}`
  g.fillText(`Laporan kas ${judul.toLowerCase()} · ${periode}`, pad, y)

  y += 70
  const row = (label: string, value: string, color = ink, bold = 700) => {
    g.fillStyle = muted
    g.font = font(500, 32)
    g.fillText(label, pad, y)
    g.fillStyle = color
    g.font = font(bold, 34)
    g.textAlign = 'right'
    g.fillText(value, W - pad, y)
    g.textAlign = 'left'
    g.strokeStyle = line
    g.beginPath()
    g.moveTo(pad, y + 24)
    g.lineTo(W - pad, y + 24)
    g.stroke()
    y += rowH + 8
  }
  row('Uang masuk', `+ ${rp(r.masuk)}`, masuk)
  row('Uang keluar', `− ${rp(r.keluar)}`, keluar)
  row(r.laba >= 0 ? 'Laba periode ini' : 'Rugi periode ini', rp(r.laba), r.laba >= 0 ? masuk : keluar, 800)
  row('Sisa kas akhir', rp(r.sisa_kas_akhir), ink, 800)

  if (r.prediksi.cukup_data) {
    y += 20
    g.fillStyle = ink
    g.font = font(800, 34)
    g.fillText('Perkiraan laba', pad, y)
    y += 56
    row('Sampai akhir bulan', rp(r.prediksi.perkiraan_akhir_bulan!), ink)
  }

  y += 30
  g.fillStyle = ink
  g.font = font(800, 34)
  g.fillText(kat.length ? 'Uang keluar terbanyak' : 'Belum ada uang keluar', pad, y)
  y += 56
  for (const k of kat) row(`${k.nama} (${k.persen}%)`, rp(k.total), keluar)

  g.fillStyle = muted
  g.font = font(500, 24)
  g.fillText(`Dibuat dengan Kas Resto, ${new Date().toLocaleString('id-ID')}`, pad, H - pad + 20)

  return new Promise((ok, fail) => c.toBlob((b) => (b ? ok(b) : fail(new Error('Gagal membuat gambar'))), 'image/png'))
}
