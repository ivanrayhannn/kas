<script setup lang="ts">
defineProps<{ title: string; lead?: string }>()
</script>

<template>
  <div class="mx-auto flex min-h-dvh max-w-md flex-col px-5 pb-10 pt-10">
    <p class="text-lg font-extrabold tracking-tight">Kas Resto</p>
    <h1 class="mt-8 text-[1.75rem] font-extrabold leading-tight tracking-tight">{{ title }}</h1>
    <p v-if="lead" class="mt-2 text-muted">{{ lead }}</p>
    <div class="mt-8"><slot /></div>
  </div>
</template>
