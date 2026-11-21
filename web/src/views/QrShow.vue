<script setup lang="ts">
import { useApp } from '../stores/app'
const s = useApp()
</script>

<template>
  <!-- Selalu terang dan kontras tinggi supaya kamera pelanggan mudah memindai. -->
  <div class="flex min-h-dvh flex-col bg-white px-5 pb-8 pt-5 text-[#1c2620]">
    <RouterLink to="/qris" class="flex min-h-11 items-center self-start rounded-lg px-2 font-semibold underline underline-offset-4">Tutup</RouterLink>
    <div class="flex flex-1 flex-col items-center justify-center text-center">
      <p class="text-sm font-semibold">Bayar ke</p>
      <h1 class="mt-1 text-[1.75rem] font-extrabold leading-tight">{{ s.store?.nama_toko }}</h1>
      <p v-if="s.store?.alamat" class="mt-1 text-sm">{{ s.store.alamat }}</p>
      <img v-if="s.store?.qr_image" :src="s.store.qr_image" :alt="`QR pembayaran ${s.store.nama_toko}`"
        width="360" height="360" class="mt-6 aspect-square w-full max-w-[360px] rounded-xl border border-[#e2dccd] object-contain p-2" />
      <div v-else class="mt-6 w-full max-w-sm rounded-xl border border-dashed border-[#bdb6a5] p-6">
        <p class="font-bold">Gambar QR belum diunggah</p>
        <p class="mt-1 text-sm">Unggah foto QRIS toko Anda di Pengaturan agar bisa ditunjukkan ke pelanggan.</p>
        <RouterLink to="/pengaturan#qr" class="btn btn-primary mt-4">Unggah QR di Pengaturan</RouterLink>
      </div>
      <p v-if="s.store?.qr_image" class="mt-6 max-w-xs text-sm">Setelah membayar, tunjukkan bukti transfer ke kasir.</p>
    </div>
  </div>
</template>
