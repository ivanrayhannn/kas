<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import Icon from '../components/Icon.vue'
import { useApp } from '../stores/app'
const s = useApp()
const items = [
  { to: '/qris', icon: 'qr', title: 'Pembayaran QRIS', text: 'Tunjukkan QR toko, periksa pelanggan yang sudah bayar' },
  { to: '/belanja', icon: 'cart', title: 'Catatan belanja', text: 'Daftar belanja bahan dan perkiraan biayanya' },
  { to: '/pengaturan', icon: 'gear', title: 'Pengaturan', text: 'Profil toko, modal awal, kategori, QR, akun' },
] as const
</script>

<template>
  <PageHeader title="Menu lainnya" />
  <nav aria-label="Menu lainnya" class="ledger card mx-4 overflow-hidden md:mx-8">
    <RouterLink v-for="i in items" :key="i.to" :to="i.to" class="flex min-h-[72px] items-center gap-4 px-4 py-3 transition-colors hover:bg-paper">
      <span class="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-paper"><Icon :name="i.icon" /></span>
      <span class="min-w-0 flex-1">
        <span class="block font-bold">{{ i.title }}
          <span v-if="i.to === '/qris' && s.summary?.pembayaran_menunggu" class="ml-1 rounded-md bg-warn-soft px-2 py-0.5 text-xs font-bold text-warn">{{ s.summary.pembayaran_menunggu }} menunggu</span>
        </span>
        <span class="block text-sm text-muted">{{ i.text }}</span>
      </span>
    </RouterLink>
  </nav>
</template>
