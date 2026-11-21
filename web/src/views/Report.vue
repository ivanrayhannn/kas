<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { addDays, isoDate, rp, tanggalPanjang, tanggalPendek } from '../lib/format'
import { reportPng } from '../lib/reportImage'
import type { Report } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const opts = [['hari', 'Hari ini'], ['7', '7 hari'], ['bulan', 'Bulan ini'], ['pilih', 'Pilih tanggal']] as const
type Periode = (typeof opts)[number][0]
const periode = ref<Periode>('hari')
const dari = ref(addDays(isoDate(), -6))
const sampai = ref(isoDate())
const data = ref<Report | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const sharing = ref(false)
const print = () => window.print()

const range = computed(() => {
  const t = isoDate()
  if (periode.value === 'hari') return { dari: t, sampai: t }
  if (periode.value === '7') return { dari: addDays(t, -6), sampai: t }
  if (periode.value === 'bulan') return { dari: t.slice(0, 8) + '01', sampai: t }
  return { dari: dari.value, sampai: sampai.value }
})
const judul = computed(() => opts.find((o) => o[0] === periode.value)![1])
const maxHarian = computed(() => Math.max(1, ...(data.value?.harian ?? []).flatMap((d) => [d.masuk, d.keluar])))

async function load() {
  loading.value = true
  error.value = null
  try {
    data.value = await api<Report>(`/report?dari=${range.value.dari}&sampai=${range.value.sampai}`)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
watch(range, load)
onMounted(load)

async function share() {
  if (!data.value || !s.store) return
  sharing.value = true
  try {
    const blob = await reportPng(data.value, s.store.nama_toko, judul.value)
    const file = new File([blob], `laporan-kas-${data.value.dari}_${data.value.sampai}.png`, { type: 'image/png' })
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file], title: `Laporan kas ${s.store.nama_toko}` })
    } else {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(file)
      a.download = file.name
      a.click()
      URL.revokeObjectURL(a.href)
      s.toast('Gambar laporan sudah diunduh.')
    }
  } catch (e) {
    if ((e as Error).name !== 'AbortError') s.toast('Laporan belum bisa dibagikan. Coba lagi.', 'error')
  } finally {
    sharing.value = false
  }
}
</script>

<template>
  <PageHeader title="Laporan" :subtitle="data ? (data.dari === data.sampai ? tanggalPanjang(data.dari) : `${tanggalPendek(data.dari)} sampai ${tanggalPendek(data.sampai)}`) : undefined" />

  <div class="no-print space-y-3 px-4 pb-4 md:px-8">
    <div class="flex flex-wrap gap-2" role="group" aria-label="Periode laporan">
      <button v-for="[v, l] in opts" :key="v" type="button" class="chip shrink-0" :aria-pressed="periode === v" @click="periode = v">{{ l }}</button>
    </div>
    <div v-if="periode === 'pilih'" class="grid grid-cols-2 gap-3">
      <div><label class="label" for="r-dari">Dari</label><input id="r-dari" v-model="dari" type="date" class="field" :max="sampai" /></div>
      <div><label class="label" for="r-sampai">Sampai</label><input id="r-sampai" v-model="sampai" type="date" class="field" :min="dari" /></div>
    </div>
  </div>

  <StateView :loading="loading" :error="error" @retry="load">
    <div v-if="data" class="space-y-4 px-4 pb-8 md:px-8">
      <section class="card p-5" aria-labelledby="ringkasan">
        <h2 id="ringkasan" class="font-bold">Ringkasan</h2>
        <p v-if="!data.jumlah_transaksi" class="mt-1 text-sm text-muted">Belum ada catatan di periode ini.</p>
        <dl class="ledger mt-3">
          <div class="flex justify-between gap-4 py-3"><dt>Uang masuk</dt><dd class="amount font-bold text-masuk">+ {{ rp(data.masuk) }}</dd></div>
          <div class="flex justify-between gap-4 py-3"><dt>Uang keluar</dt><dd class="amount font-bold text-keluar">− {{ rp(data.keluar) }}</dd></div>
          <div class="flex justify-between gap-4 py-3">
            <dt class="font-bold">{{ data.laba >= 0 ? 'Laba' : 'Rugi' }} <span class="block text-sm font-normal text-muted">Uang masuk dikurangi uang keluar</span></dt>
            <dd class="amount text-xl font-extrabold" :class="data.laba >= 0 ? 'text-masuk' : 'text-keluar'">{{ rp(data.laba) }}</dd>
          </div>
          <div class="flex justify-between gap-4 py-3">
            <dt>Sisa kas akhir periode <span class="block text-sm text-muted">Awal periode {{ rp(data.sisa_kas_awal) }}</span></dt>
            <dd class="amount font-bold">{{ rp(data.sisa_kas_akhir) }}</dd>
          </div>
        </dl>
      </section>

      <section class="card p-5" aria-labelledby="prediksi">
        <h2 id="prediksi" class="font-bold">Prediksi Laba</h2>
        <template v-if="data.prediksi.cukup_data">
          <p class="mt-1 text-sm text-muted">Dari rata-rata {{ data.prediksi.dasar_hari }} hari terakhir: laba sekitar {{ rp(data.prediksi.rata_rata_laba_harian!) }} per hari. Perkiraan, bukan kepastian.</p>
          <dl class="mt-4 grid grid-cols-2 gap-4">
            <div><dt class="text-sm text-muted">7 hari ke depan</dt><dd class="amount text-lg font-extrabold" :class="data.prediksi.perkiraan_7_hari! < 0 ? 'text-keluar' : ''">{{ rp(data.prediksi.perkiraan_7_hari!) }}</dd></div>
            <div><dt class="text-sm text-muted">Sampai akhir bulan</dt><dd class="amount text-lg font-extrabold" :class="data.prediksi.perkiraan_akhir_bulan! < 0 ? 'text-keluar' : ''">{{ rp(data.prediksi.perkiraan_akhir_bulan!) }}</dd></div>
          </dl>
          <div v-if="data.prediksi.persen_balik_modal !== null" class="mt-5">
            <p class="flex justify-between text-sm"><span class="font-semibold">Modal sudah kembali</span><span class="amount font-bold">{{ data.prediksi.persen_balik_modal }}%</span></p>
            <div class="mt-2 h-3 rounded bg-paper" role="img" :aria-label="`Modal sudah kembali ${data.prediksi.persen_balik_modal} persen`">
              <div class="h-3 rounded bg-masuk" :style="{ width: `${data.prediksi.persen_balik_modal}%` }"></div>
            </div>
            <p class="mt-2 text-sm text-muted">
              <template v-if="data.prediksi.perkiraan_hari_balik_modal === 0">Laba sudah melebihi modal awal.</template>
              <template v-else-if="data.prediksi.perkiraan_hari_balik_modal">Bila pola ini berlanjut, modal kembali dalam sekitar {{ data.prediksi.perkiraan_hari_balik_modal }} hari.</template>
              <template v-else>Laba harian belum positif, jadi belum bisa diperkirakan kapan modal kembali.</template>
            </p>
          </div>
        </template>
        <p v-else class="mt-1 text-sm text-muted">Butuh catatan minimal {{ data.prediksi.min_hari }} hari berbeda dalam 14 hari terakhir. Sekarang baru {{ data.prediksi.hari_data }} hari.</p>
      </section>

      <section v-for="[key, title, color] in [['kategori_keluar', 'Uang keluar per kategori', 'bg-keluar'], ['kategori_masuk', 'Uang masuk per kategori', 'bg-masuk']] as const"
        :key="key" class="card p-5" :aria-labelledby="key">
        <h2 :id="key" class="font-bold">{{ title }}</h2>
        <p v-if="!data[key].length" class="mt-1 text-sm text-muted">Belum ada di periode ini.</p>
        <ul v-else class="mt-4 space-y-4">
          <li v-for="k in data[key]" :key="k.nama">
            <p class="flex justify-between gap-3 text-[0.9375rem]">
              <span class="font-semibold">{{ k.nama }} <span class="font-normal text-muted">· {{ k.jumlah }}x</span></span>
              <span class="amount shrink-0 font-bold">{{ rp(k.total) }} <span class="font-normal text-muted">{{ k.persen }}%</span></span>
            </p>
            <div class="mt-1.5 h-2.5 rounded bg-paper" aria-hidden="true"><div class="h-2.5 rounded" :class="color" :style="{ width: `${Math.max(k.persen, 2)}%` }"></div></div>
          </li>
        </ul>
      </section>

      <section v-if="data.harian.length > 1" class="card overflow-hidden" aria-labelledby="harian">
        <h2 id="harian" class="px-5 pt-5 font-bold">Laporan harian</h2>
        <div class="overflow-x-auto">
          <table class="mt-3 w-full min-w-[440px] text-sm">
            <thead class="text-left text-muted">
              <tr class="border-b border-line"><th scope="col" class="px-5 py-2 font-semibold">Tanggal</th><th scope="col" class="px-2 py-2 text-right font-semibold">Masuk</th><th scope="col" class="px-2 py-2 text-right font-semibold">Keluar</th><th scope="col" class="px-5 py-2 text-right font-semibold">Sisa kas</th></tr>
            </thead>
            <tbody>
              <tr v-for="d in [...data.harian].reverse()" :key="d.tanggal" class="border-b border-line last:border-0">
                <th scope="row" class="px-5 py-2.5 text-left font-semibold">
                  {{ tanggalPendek(d.tanggal) }}
                  <span class="mt-1 flex h-1.5 gap-0.5" aria-hidden="true">
                    <span class="rounded bg-masuk" :style="{ width: `${(d.masuk / maxHarian) * 64}px` }"></span>
                    <span class="rounded bg-keluar" :style="{ width: `${(d.keluar / maxHarian) * 64}px` }"></span>
                  </span>
                </th>
                <td class="amount px-2 py-2.5 text-right text-masuk">{{ d.masuk ? rp(d.masuk) : '·' }}</td>
                <td class="amount px-2 py-2.5 text-right text-keluar">{{ d.keluar ? rp(d.keluar) : '·' }}</td>
                <td class="amount px-5 py-2.5 text-right font-bold">{{ rp(d.sisa_kas) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="no-print grid grid-cols-2 gap-3">
        <button type="button" class="btn btn-primary" :disabled="sharing" @click="share">{{ sharing ? 'Menyiapkan…' : 'Bagikan gambar' }}</button>
        <button type="button" class="btn btn-ghost" @click="print">Simpan PDF</button>
      </div>
      <p class="no-print text-sm text-muted">Bagikan gambar membuka WhatsApp atau aplikasi lain di ponsel. Simpan PDF membuka jendela cetak; pilih "Simpan sebagai PDF".</p>
    </div>
  </StateView>
</template>
