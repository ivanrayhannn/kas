<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import MoneyInput from '../components/MoneyInput.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { rp, waktu } from '../lib/format'
import type { Payment, Summary } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const items = ref<Payment[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const tab = ref<'menunggu' | 'selesai'>('menunggu')
const nominal = ref<number | null>(null)
const nama = ref('')
const adding = ref(false)
const formError = ref('')
const busyId = ref('')
const rejectId = ref('')
const alasan = ref('')

const shown = computed(() => items.value.filter((p) => (tab.value === 'menunggu' ? p.status === 'menunggu' : p.status !== 'menunggu')))
const waitingCount = computed(() => items.value.filter((p) => p.status === 'menunggu').length)
const statusLabel = { menunggu: 'Menunggu', terverifikasi: 'Terverifikasi', ditolak: 'Ditolak' }

async function load() {
  loading.value = true
  error.value = null
  try { items.value = await api<Payment[]>('/payments') }
  catch (e) { error.value = (e as Error).message }
  finally { loading.value = false }
}

async function add() {
  formError.value = ''
  if (!nominal.value) return (formError.value = 'Isi nominal yang dibayar pelanggan.')
  adding.value = true
  try {
    const p = await api<Payment>('/payments', { method: 'POST', body: { nominal: nominal.value, nama_pelanggan: nama.value || null } })
    items.value.unshift(p)
    nominal.value = null
    nama.value = ''
    tab.value = 'menunggu'
    if (s.summary) s.summary.pembayaran_menunggu++
    s.toast('Klaim dicatat. Cek mutasi rekening, lalu tekan Verifikasi.')
  } catch (e) {
    formError.value = (e as Error).message
  } finally {
    adding.value = false
  }
}

function replace(p: Payment) {
  items.value = items.value.map((x) => (x.id === p.id ? p : x))
}

async function verify(p: Payment) {
  busyId.value = p.id
  try {
    const r = await api<{ payment: Payment; summary: Summary }>(`/payments/${p.id}/verify`, { method: 'POST', body: {} })
    replace(r.payment)
    s.applySummary(r.summary)
    s.toast(`Terverifikasi. ${rp(p.nominal)} tercatat sebagai uang masuk.`)
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    busyId.value = ''
  }
}

async function reject(p: Payment) {
  if (!alasan.value.trim()) return
  busyId.value = p.id
  try {
    const r = await api<{ payment: Payment }>(`/payments/${p.id}/reject`, { method: 'POST', body: { alasan: alasan.value } })
    replace(r.payment)
    if (s.summary) s.summary.pembayaran_menunggu = Math.max(0, s.summary.pembayaran_menunggu - 1)
    rejectId.value = ''
    alasan.value = ''
    s.toast('Klaim ditolak. Sisa kas tidak berubah.')
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    busyId.value = ''
  }
}
onMounted(load)
</script>

<template>
  <PageHeader title="Pembayaran QRIS" back="/lainnya" />

  <div class="space-y-4 px-4 pb-8 md:px-8">
    <RouterLink to="/qris/tampil" class="btn btn-primary min-h-16 w-full text-lg">Tunjukkan QR ke pelanggan</RouterLink>

    <form class="card space-y-4 p-5" novalidate @submit.prevent="add">
      <h2 class="font-bold">Catat pelanggan yang sudah bayar</h2>
      <div>
        <label class="label" for="p-nominal">Nominal yang dibayar</label>
        <MoneyInput id="p-nominal" v-model="nominal" placeholder="0" />
      </div>
      <div>
        <label class="label" for="p-nama">Nama atau catatan <span class="font-normal text-muted">(boleh kosong)</span></label>
        <input id="p-nama" v-model="nama" class="field" maxlength="100" placeholder="Contoh: Meja 4" />
      </div>
      <p v-if="formError" class="error-text" role="alert">{{ formError }}</p>
      <button class="btn btn-ghost w-full" :disabled="adding">{{ adding ? 'Menyimpan…' : 'Tambah ke daftar periksa' }}</button>
    </form>

    <div class="grid grid-cols-2 gap-2 rounded-xl bg-surface p-1 ring-1 ring-line" role="group" aria-label="Status pembayaran">
      <button type="button" :aria-pressed="tab === 'menunggu'" class="min-h-11 rounded-lg font-bold transition-colors aria-pressed:bg-ink aria-pressed:text-on-ink" @click="tab = 'menunggu'">
        Menunggu{{ waitingCount ? ` (${waitingCount})` : '' }}</button>
      <button type="button" :aria-pressed="tab === 'selesai'" class="min-h-11 rounded-lg font-bold transition-colors aria-pressed:bg-ink aria-pressed:text-on-ink" @click="tab = 'selesai'">Sudah diperiksa</button>
    </div>
  </div>

  <StateView :loading="loading" :error="error" :empty="!shown.length"
    :empty-title="tab === 'menunggu' ? 'Tidak ada yang perlu diperiksa' : 'Belum ada yang diperiksa'"
    :empty-text="tab === 'menunggu' ? 'Saat pelanggan bilang sudah bayar lewat QR, catat di formulir di atas.' : 'Pembayaran yang diverifikasi atau ditolak akan muncul di sini.'"
    @retry="load">
    <ul class="ledger card mx-4 overflow-hidden md:mx-8">
      <li v-for="p in shown" :key="p.id" class="p-4" :class="p.status === 'menunggu' ? 'bg-warn-soft/40' : ''">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="amount text-lg font-extrabold">{{ rp(p.nominal) }}</p>
            <p class="truncate text-sm text-muted">{{ p.nama_pelanggan || 'Tanpa nama' }} · {{ waktu(p.created_at) }}</p>
          </div>
          <span class="shrink-0 rounded-md px-2 py-1 text-xs font-bold"
            :class="{ 'bg-warn-soft text-warn': p.status === 'menunggu', 'bg-masuk-soft text-masuk': p.status === 'terverifikasi', 'bg-keluar-soft text-keluar': p.status === 'ditolak' }">
            {{ statusLabel[p.status] }}</span>
        </div>
        <p v-if="p.status === 'terverifikasi'" class="mt-2 text-sm text-masuk">Sudah tercatat sebagai uang masuk.
          <RouterLink v-if="p.transaction_id" :to="`/riwayat/${p.transaction_id}`" class="font-bold underline underline-offset-4">Lihat catatan</RouterLink></p>
        <p v-if="p.status === 'ditolak'" class="mt-2 text-sm"><span class="text-muted">Alasan:</span> {{ p.alasan_tolak }}</p>

        <template v-if="p.status === 'menunggu'">
          <form v-if="rejectId === p.id" class="mt-3 space-y-3" @submit.prevent="reject(p)">
            <div>
              <label class="label" :for="`alasan-${p.id}`">Alasan menolak</label>
              <input :id="`alasan-${p.id}`" v-model="alasan" class="field" maxlength="200" placeholder="Contoh: tidak ada di mutasi rekening" required />
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button type="button" class="btn btn-ghost" @click="rejectId = ''">Batal</button>
              <button class="btn btn-keluar" :disabled="!alasan.trim() || busyId === p.id">Tolak</button>
            </div>
          </form>
          <div v-else class="mt-3 grid grid-cols-2 gap-2">
            <button type="button" class="btn btn-danger" :disabled="busyId === p.id" @click="rejectId = p.id; alasan = ''">Tolak</button>
            <button type="button" class="btn btn-masuk" :disabled="busyId === p.id" @click="verify(p)">{{ busyId === p.id ? 'Memproses…' : 'Verifikasi' }}</button>
          </div>
        </template>
      </li>
    </ul>
  </StateView>
</template>
