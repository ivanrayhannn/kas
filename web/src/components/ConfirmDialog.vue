<script setup lang="ts">
import { ref, watch } from 'vue'

// Dialog bawaan browser: fokus terkunci di dalam dan Escape menutup.
const open = defineModel<boolean>({ required: true })
defineProps<{ title: string; confirmLabel: string; danger?: boolean; busy?: boolean }>()
const emit = defineEmits<{ confirm: [] }>()
const el = ref<HTMLDialogElement>()

watch(open, (v) => (v ? el.value?.showModal() : el.value?.close()))
</script>

<template>
  <dialog ref="el" class="m-auto w-[calc(100%-32px)] max-w-sm rounded-2xl border border-line bg-surface p-0 text-ink"
    :aria-labelledby="'dlg-' + title" @close="open = false" @click.self="open = false">
    <form method="dialog" class="p-5" @submit.prevent="emit('confirm')">
      <h2 :id="'dlg-' + title" class="text-lg font-extrabold">{{ title }}</h2>
      <div class="mt-2 text-sm text-muted"><slot /></div>
      <div class="mt-5 grid grid-cols-2 gap-3">
        <button type="button" class="btn btn-ghost" @click="open = false">Batal</button>
        <button class="btn" :class="danger ? 'btn-keluar' : 'btn-primary'" :disabled="busy">{{ busy ? 'Memproses…' : confirmLabel }}</button>
      </div>
    </form>
  </dialog>
</template>
