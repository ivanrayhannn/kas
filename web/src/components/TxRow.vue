<script setup lang="ts">
import { rpSigned } from '../lib/format'
import type { Transaction } from '../lib/types'

defineProps<{ tx: Transaction }>()
const sumberLabel = { manual: '', qris: 'QRIS', belanja: 'Belanja' } as const
</script>

<template>
  <RouterLink :to="`/riwayat/${tx.id}`" class="flex min-h-16 items-center gap-3 px-4 py-3 transition-colors hover:bg-paper">
    <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-lg font-extrabold"
      :class="tx.jenis === 'masuk' ? 'bg-masuk-soft text-masuk' : 'bg-keluar-soft text-keluar'" aria-hidden="true">
      {{ tx.jenis === 'masuk' ? '+' : '−' }}
    </span>
    <span class="min-w-0 flex-1">
      <span class="block truncate font-semibold">{{ tx.kategori }}
        <span v-if="sumberLabel[tx.sumber]" class="ml-1 rounded bg-paper px-1.5 py-0.5 align-middle text-xs font-bold text-muted">{{ sumberLabel[tx.sumber] }}</span>
      </span>
      <span v-if="tx.catatan" class="block truncate text-sm text-muted">{{ tx.catatan }}</span>
    </span>
    <span class="amount shrink-0 font-bold" :class="tx.jenis === 'masuk' ? 'text-masuk' : 'text-keluar'">
      <span class="sr-only">{{ tx.jenis === 'masuk' ? 'Uang masuk' : 'Uang keluar' }}</span>{{ rpSigned(tx.nominal, tx.jenis) }}
    </span>
  </RouterLink>
</template>
