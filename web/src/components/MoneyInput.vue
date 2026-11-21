<script setup lang="ts">
import { computed } from 'vue'
import { parseRupiah } from '../lib/format'

const model = defineModel<number | null>({ required: true })
defineProps<{ id: string; placeholder?: string; describedby?: string }>()
const shown = computed(() => (model.value === null ? '' : new Intl.NumberFormat('id-ID').format(model.value)))
function onInput(e: Event) {
  const el = e.target as HTMLInputElement
  model.value = el.value.trim() === '' ? null : parseRupiah(el.value)
  el.value = shown.value
}
</script>

<template>
  <div class="relative">
    <span class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 font-semibold text-muted" aria-hidden="true">Rp</span>
    <input :id="id" class="field amount pl-11" inputmode="numeric" autocomplete="off" :value="shown"
      :placeholder="placeholder" :aria-describedby="describedby" @input="onInput" />
  </div>
</template>
