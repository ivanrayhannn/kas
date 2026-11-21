<script setup lang="ts">
// Satu tempat untuk tiga keadaan data: memuat, gagal, dan kosong.
defineProps<{ loading?: boolean; error?: string | null; empty?: boolean; emptyTitle?: string; emptyText?: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <div v-if="loading" class="px-4 py-10 text-center text-muted md:px-8" role="status">
    <span class="inline-block h-6 w-6 animate-spin rounded-full border-[3px] border-line border-t-ink align-middle" aria-hidden="true"></span>
    <span class="ml-3 align-middle font-semibold">Memuat…</span>
  </div>
  <div v-else-if="error" class="mx-4 rounded-xl border border-keluar/30 bg-keluar-soft p-5 md:mx-8" role="alert">
    <p class="font-bold text-keluar">Data belum bisa dimuat</p>
    <p class="mt-1 text-sm">{{ error }}</p>
    <button type="button" class="btn btn-ghost mt-4 bg-surface" @click="$emit('retry')">Coba lagi</button>
  </div>
  <div v-else-if="empty" class="mx-4 rounded-xl border border-dashed border-line px-5 py-8 text-center md:mx-8">
    <p class="font-bold">{{ emptyTitle }}</p>
    <p v-if="emptyText" class="mx-auto mt-1 max-w-sm text-sm text-muted">{{ emptyText }}</p>
    <slot name="empty-action" />
  </div>
  <slot v-else />
</template>
