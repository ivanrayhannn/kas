<script setup lang="ts">
import { onMounted, ref } from 'vue'
import StateView from '../components/StateView.vue'
import TxRow from '../components/TxRow.vue'
import { api } from '../lib/api'
import { rp } from '../lib/format'
import type { Transaction } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const recent = ref<Transaction[]>([])
const loading = ref(!s.summary)
const error = ref<string | null>(null)

async function load() {
  error.value = null
  s.loadCategories().catch(() => {}) // disimpan di ponsel untuk mencatat saat offline
  try {
    const [, list] = await Promise.all([s.loadSummary(), api<{ items: Transaction[] }>('/transactions?limit=5')])
    recent.value = list.items
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <div class="px-4 pt-5 md:px-8 md:pt-8">
    <p class="text-sm font-semibold text-muted">{{ new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) }}</p>
    <h1 class="text-[1.375rem] font-extrabold tracking-tight">{{ s.store?.nama_toko }}</h1>
  </div>

  <StateView :loading="loading" :error="!s.summary ? error : null" @retry="load">
    <div v-if="s.summary" class="space-y-4 px-4 pb-6 pt-4 md:px-8">
      <div v-if="s.summary.kas_menipis" class="rounded-xl border border-warn/30 bg-warn-soft p-4 text-warn" role="alert">
        <p class="font-extrabold">Kas Menipis</p>
        <p class="mt-1 text-sm">Sisa kas sudah di bawah {{ rp(s.summary.ambang_kas_menipis) }}{{ s.summary.ambang_bawaan ? ' (batas bawaan)' : '' }}.
          Kurangi pengeluaran yang belum mendesak atau tambah modal.
          <RouterLink to="/pengaturan#kas" class="font-bold underline underline-offset-4">Atur batas</RouterLink></p>
      </div>

      <section class="card p-5" aria-labelledby="sisa-kas">
        <h2 id="sisa-kas" class="text-sm font-bold text-muted">Sisa Kas</h2>
        <p class="amount mt-1 whitespace-normal break-words text-[2.5rem] font-extrabold leading-none tracking-tight md:text-5xl"
          :class="s.summary.sisa_kas < 0 ? 'text-keluar' : ''">{{ rp(s.summary.sisa_kas) }}</p>
        <p v-if="s.summary.jumlah_transaksi === 0" class="mt-3 text-sm text-muted">
          Belum ada transaksi. Angka ini masih sama dengan modal awal.
        </p>
        <dl class="ledger mt-5 text-[0.9375rem]">
          <div class="flex items-start justify-between gap-4 py-3">
            <dt><span class="font-semibold">Modal Awal</span><span class="block text-sm text-muted">Uang kas saat mulai mencatat</span></dt>
            <dd class="amount shrink-0 font-bold">{{ rp(s.summary.modal_awal) }}</dd>
          </div>
          <div class="flex items-start justify-between gap-4 py-3">
            <dt><span class="font-semibold">Uang Masuk</span><span class="block text-sm text-muted">Semua penjualan dan uang diterima</span></dt>
            <dd class="amount shrink-0 font-bold text-masuk">+ {{ rp(s.summary.total_masuk) }}</dd>
          </div>
          <div class="flex items-start justify-between gap-4 py-3">
            <dt><span class="font-semibold">Terpakai untuk Operasional</span><span class="block text-sm text-muted">Semua uang keluar: bahan, gaji, transport</span></dt>
            <dd class="amount shrink-0 font-bold text-keluar">− {{ rp(s.summary.terpakai_operasional) }}</dd>
          </div>
        </dl>
      </section>

      <div class="no-print grid grid-cols-2 gap-3">
        <RouterLink :to="{ name: 'catat', query: { jenis: 'masuk' } }" class="btn btn-masuk min-h-16 text-lg">+ Uang Masuk</RouterLink>
        <RouterLink :to="{ name: 'catat', query: { jenis: 'keluar' } }" class="btn btn-keluar min-h-16 text-lg">− Uang Keluar</RouterLink>
      </div>

      <p v-if="s.outbox.length" class="rounded-xl border border-line bg-surface p-4 text-sm" role="status">
        <strong>{{ s.outbox.length }} catatan belum terkirim</strong> karena tidak ada internet. Akan dikirim otomatis saat online, lalu sisa kas ikut diperbarui.
      </p>

      <RouterLink v-if="s.summary.pembayaran_menunggu" to="/qris"
        class="flex min-h-14 items-center justify-between gap-3 rounded-xl border border-warn/30 bg-warn-soft px-4 py-3 text-warn transition-colors hover:border-warn">
        <span class="font-semibold">{{ s.summary.pembayaran_menunggu }} pembayaran QRIS menunggu diperiksa</span>
        <span class="font-bold underline underline-offset-4">Periksa</span>
      </RouterLink>

      <section class="card" aria-labelledby="hari-ini">
        <h2 id="hari-ini" class="px-4 pt-4 font-bold">Hari ini</h2>
        <div class="grid grid-cols-2 gap-3 p-4">
          <div><p class="text-sm text-muted">Masuk</p><p class="amount text-lg font-bold text-masuk">{{ rp(s.summary.hari_ini.masuk) }}</p></div>
          <div><p class="text-sm text-muted">Keluar</p><p class="amount text-lg font-bold text-keluar">{{ rp(s.summary.hari_ini.keluar) }}</p></div>
        </div>
      </section>

      <section class="card overflow-hidden" aria-labelledby="terakhir">
        <div class="flex items-center justify-between px-4 pt-4">
          <h2 id="terakhir" class="font-bold">Catatan terakhir</h2>
          <RouterLink v-if="recent.length" to="/riwayat" class="flex min-h-11 items-center font-semibold underline underline-offset-4">Lihat semua</RouterLink>
        </div>
        <p v-if="!recent.length" class="px-4 pb-5 pt-2 text-sm text-muted">Belum ada catatan. Tekan Uang Masuk saat ada penjualan pertama.</p>
        <div v-else class="ledger mt-2">
          <TxRow v-for="t in recent" :key="t.id" :tx="t" />
        </div>
      </section>
    </div>
  </StateView>
</template>
