<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { rp, tanggalPanjang, waktu } from '../lib/format'
import type { Summary, Transaction } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const route = useRoute()
const router = useRouter()
const tx = ref<Transaction | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const askDelete = ref(false)
const deleting = ref(false)
const sumberLabel = { manual: 'Dicatat manual', qris: 'Otomatis dari pembayaran QRIS', belanja: 'Otomatis dari catatan belanja' }

async function load() {
  loading.value = true
  error.value = null
  try { tx.value = await api<Transaction>(`/transactions/${route.params.id}`) }
  catch (e) { error.value = (e as Error).message }
  finally { loading.value = false }
}

async function remove() {
  deleting.value = true
  try {
    const r = await api<{ summary: Summary }>(`/transactions/${route.params.id}`, { method: 'DELETE' })
    s.applySummary(r.summary)
    s.toast('Catatan dihapus. Sisa kas sudah disesuaikan.')
    router.replace('/riwayat')
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    deleting.value = false
    askDelete.value = false
  }
}
onMounted(load)
</script>

<template>
  <PageHeader title="Detail catatan" back="/riwayat" />
  <StateView :loading="loading" :error="error" @retry="load">
    <div v-if="tx" class="px-4 pb-8 md:px-8">
      <section class="card p-5">
        <p class="text-sm font-bold" :class="tx.jenis === 'masuk' ? 'text-masuk' : 'text-keluar'">{{ tx.jenis === 'masuk' ? 'Uang Masuk' : 'Uang Keluar' }}</p>
        <p class="amount mt-1 text-4xl font-extrabold">{{ rp(tx.nominal) }}</p>
        <dl class="ledger mt-5">
          <div class="flex justify-between gap-4 py-3"><dt class="text-muted">Kategori</dt><dd class="text-right font-semibold">{{ tx.kategori }}</dd></div>
          <div class="flex justify-between gap-4 py-3"><dt class="text-muted">Tanggal</dt><dd class="text-right font-semibold">{{ tanggalPanjang(tx.tanggal) }}</dd></div>
          <div class="flex justify-between gap-4 py-3"><dt class="text-muted">Catatan</dt><dd class="text-right font-semibold">{{ tx.catatan || 'Tidak ada' }}</dd></div>
          <div class="flex justify-between gap-4 py-3"><dt class="text-muted">Asal</dt><dd class="text-right font-semibold">{{ sumberLabel[tx.sumber] }}</dd></div>
          <div class="flex justify-between gap-4 py-3"><dt class="text-muted">Dicatat</dt><dd class="text-right">{{ waktu(tx.created_at) }}</dd></div>
          <div v-if="tx.updated_at.slice(0, 19) !== tx.created_at.slice(0, 19)" class="flex justify-between gap-4 py-3">
            <dt class="text-muted">Terakhir diperbaiki</dt><dd class="text-right">{{ waktu(tx.updated_at) }}</dd></div>
        </dl>
      </section>
      <p v-if="tx.sumber !== 'manual'" class="mt-4 text-sm text-muted">
        Catatan otomatis tidak bisa diubah. Bila dihapus, {{ tx.sumber === 'qris' ? 'pembayarannya kembali ke status Menunggu' : 'daftar belanjanya kembali bisa diubah' }}.
      </p>
      <div class="mt-5 grid grid-cols-2 gap-3">
        <RouterLink v-if="tx.sumber === 'manual'" :to="`/catat/${tx.id}`" class="btn btn-primary">Perbaiki</RouterLink>
        <button type="button" class="btn btn-danger" :class="tx.sumber !== 'manual' ? 'col-span-2' : ''" @click="askDelete = true">Hapus</button>
      </div>
    </div>
  </StateView>
  <ConfirmDialog v-model="askDelete" title="Hapus catatan ini?" confirm-label="Ya, hapus" danger :busy="deleting" @confirm="remove">
    {{ tx ? `${tx.jenis === 'masuk' ? 'Uang masuk' : 'Uang keluar'} ${rp(tx.nominal)} akan dihapus dan sisa kas dihitung ulang.` : '' }}
  </ConfirmDialog>
</template>
