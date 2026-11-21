<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const step = ref(0)
const slides = [
  { title: 'Catat jualan dalam hitungan detik', text: 'Tekan Uang Masuk, ketik nominal, pilih kategori, simpan. Selesai.', demo: 'catat' },
  { title: 'Sisa kas langsung kelihatan', text: 'Setiap catatan langsung mengubah angka sisa kas. Tidak perlu hitung manual di buku.', demo: 'kas' },
  { title: 'Laporan dan perkiraan laba', text: 'Lihat uang paling banyak habis di mana, dan berapa perkiraan laba bulan ini.', demo: 'laporan' },
]
function finish(to: 'daftar' | 'masuk') {
  localStorage.setItem('kas.welcomed', '1')
  router.push({ name: to })
}
</script>

<template>
  <div class="mx-auto flex min-h-dvh max-w-md flex-col px-5 pb-8 pt-8">
    <div class="flex items-center justify-between">
      <p class="text-lg font-extrabold tracking-tight">Kas Resto</p>
      <button type="button" class="min-h-11 px-2 font-semibold text-muted hover:text-ink" @click="finish('masuk')">Sudah punya akun</button>
    </div>

    <section class="mt-10 flex-1" aria-roledescription="langkah" :aria-label="`Langkah ${step + 1} dari 3`">
      <div class="card p-5" aria-hidden="true">
        <template v-if="slides[step].demo === 'catat'">
          <p class="text-sm font-semibold text-masuk">Uang Masuk · Penjualan</p>
          <p class="amount mt-2 text-4xl font-extrabold">Rp 85.000</p>
          <div class="mt-4 grid grid-cols-3 gap-2 text-center text-lg font-bold">
            <span v-for="k in ['1','2','3','4','5','6']" :key="k" class="rounded-lg bg-paper py-2">{{ k }}</span>
          </div>
        </template>
        <template v-else-if="slides[step].demo === 'kas'">
          <p class="text-sm font-semibold text-muted">Sisa kas</p>
          <p class="amount mt-1 text-4xl font-extrabold">Rp 1.250.000</p>
          <div class="ledger mt-4 text-sm">
            <p class="flex justify-between py-2"><span>Modal awal</span><span class="amount font-bold">Rp 1.000.000</span></p>
            <p class="flex justify-between py-2"><span>Uang masuk</span><span class="amount font-bold text-masuk">+ Rp 650.000</span></p>
            <p class="flex justify-between py-2"><span>Terpakai</span><span class="amount font-bold text-keluar">− Rp 400.000</span></p>
          </div>
        </template>
        <template v-else>
          <p class="text-sm font-semibold text-muted">Uang keluar terbanyak</p>
          <div class="mt-3 space-y-3 text-sm">
            <div v-for="[n, w] in [['Bahan Baku', '78%'], ['Gaji Karyawan', '46%'], ['Transportasi', '18%']]" :key="n">
              <p class="flex justify-between font-semibold"><span>{{ n }}</span></p>
              <div class="mt-1 h-2.5 rounded bg-paper"><div class="h-2.5 rounded bg-keluar" :style="{ width: w }"></div></div>
            </div>
          </div>
        </template>
      </div>
      <p class="mt-2 text-xs text-muted">Contoh tampilan</p>
      <h1 class="mt-8 text-[1.75rem] font-extrabold leading-tight tracking-tight">{{ slides[step].title }}</h1>
      <p class="mt-3 text-muted">{{ slides[step].text }}</p>
    </section>

    <div class="mt-8 flex items-center gap-2" aria-hidden="true">
      <span v-for="i in 3" :key="i" class="h-1.5 rounded-full transition-all" :class="i - 1 === step ? 'w-8 bg-ink' : 'w-3 bg-line'"></span>
    </div>
    <div class="mt-6 grid gap-3">
      <button v-if="step < 2" type="button" class="btn btn-primary" @click="step++">Lanjut</button>
      <button v-else type="button" class="btn btn-primary" @click="finish('daftar')">Buat akun</button>
      <button v-if="step > 0" type="button" class="btn btn-ghost" @click="step--">Sebelumnya</button>
    </div>
  </div>
</template>
