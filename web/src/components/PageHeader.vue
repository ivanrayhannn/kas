<script setup lang="ts">
import { useRouter } from 'vue-router'
import Icon from './Icon.vue'

const props = defineProps<{ title: string; back?: string; subtitle?: string }>()
const router = useRouter()
const goBack = () => (window.history.state?.back ? router.back() : router.push(props.back || '/'))
</script>

<template>
  <header class="flex items-start gap-2 px-4 pb-3 pt-5 md:px-8 md:pt-8">
    <button v-if="back" type="button" class="no-print -ml-2 grid h-11 w-11 shrink-0 place-items-center rounded-lg hover:bg-surface"
      aria-label="Kembali" @click="goBack"><Icon name="back" /></button>
    <div class="min-w-0 flex-1 pt-1.5">
      <h1 class="text-[1.375rem] font-extrabold leading-tight tracking-tight">{{ title }}</h1>
      <p v-if="subtitle" class="mt-0.5 text-sm text-muted">{{ subtitle }}</p>
    </div>
    <div class="no-print flex shrink-0 gap-2"><slot /></div>
  </header>
</template>
