<script setup lang="ts">
// Ikon digambar sendiri, satu gaya garis 2px, hanya untuk menu yang selalu disertai teks.
defineProps<{ name: 'home' | 'list' | 'plus' | 'chart' | 'menu' | 'qr' | 'cart' | 'gear' | 'back' | 'search' | 'check' | 'x' }>()
</script>

<template>
  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <template v-if="name === 'home'"><path d="M3 11 12 4l9 7" /><path d="M5 10v10h14V10" /><path d="M10 20v-6h4v6" /></template>
    <template v-else-if="name === 'list'"><path d="M5 4h14v16H5z" /><path d="M9 9h6M9 13h6M9 17h3" /></template>
    <template v-else-if="name === 'plus'"><path d="M12 5v14M5 12h14" /></template>
    <template v-else-if="name === 'chart'"><path d="M4 20h16" /><path d="M7 16v-5M12 16V7M17 16v-8" /></template>
    <template v-else-if="name === 'menu'"><path d="M4 7h16M4 12h16M4 17h16" /></template>
    <template v-else-if="name === 'qr'"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4z" /><path d="M14 14h2v2h-2zM18 18h2v2h-2zM14 18h2M18 14h2" /></template>
    <template v-else-if="name === 'cart'"><path d="M3 4h2l2 11h11l2-8H6.5" /><circle cx="9" cy="19" r="1.4" /><circle cx="17" cy="19" r="1.4" /></template>
    <template v-else-if="name === 'gear'"><circle cx="12" cy="12" r="3" /><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8" /></template>
    <template v-else-if="name === 'back'"><path d="M15 5l-7 7 7 7" /></template>
    <template v-else-if="name === 'search'"><circle cx="11" cy="11" r="6" /><path d="m20 20-4.5-4.5" /></template>
    <template v-else-if="name === 'check'"><path d="m5 12 5 5 9-10" /></template>
    <template v-else-if="name === 'x'"><path d="M6 6l12 12M18 6 6 18" /></template>
  </svg>
</template>
