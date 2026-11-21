<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { addDays, isoDate, rp, tanggalPanjang } from '../lib/format'
import type { ShoppingList } from '../lib/types'

const router = useRouter()
const lists = ref<ShoppingList[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const judul = ref('Belanja besok pagi')
const tanggal = ref(addDays(isoDate(), 1))
const creating = ref(false)
const formError = ref('')

async function load() {
  loading.value = true
  error.value = null
  try { lists.value = await api<ShoppingList[]>('/shopping-lists') }
  catch (e) { error.value = (e as Error).message }
  finally { loading.value = false }
}

async function create() {
  formError.value = ''
  if (!judul.value.trim()) return (formError.value = 'Beri nama daftar belanja.')
  creating.value = true
  try {
    const l = await api<ShoppingList>('/shopping-lists', { method: 'POST', body: { judul: judul.value, rencana_tanggal: tanggal.value } })
    router.push(`/belanja/${l.id}`)
  } catch (e) {
    formError.value = (e as Error).message
  } finally {
    creating.value = false
  }
}
onMounted(load)
</script>

<template>
  <PageHeader title="Catatan belanja" back="/lainnya" />

  <form class="card mx-4 space-y-4 p-5 md:mx-8" novalidate @submit.prevent="create">
    <h2 class="font-bold">Buat daftar baru</h2>
    <div class="grid gap-4 sm:grid-cols-[1fr_180px]">
      <div><label class="label" for="judul">Nama daftar</label><input id="judul" v-model="judul" class="field" maxlength="100" /></div>
      <div><label class="label" for="tgl">Rencana belanja</label><input id="tgl" v-model="tanggal" type="date" class="field" /></div>
    </div>
    <p v-if="formError" class="error-text" role="alert">{{ formError }}</p>
    <button class="btn btn-primary w-full" :disabled="creating">{{ creating ? 'Membuat…' : 'Buat daftar dan isi barang' }}</button>
  </form>

  <h2 class="px-4 pb-2 pt-6 font-bold md:px-8">Daftar Anda</h2>
  <StateView :loading="loading" :error="error" :empty="!lists.length" empty-title="Belum ada daftar belanja"
    empty-text="Tulis barang yang mau dibeli supaya tidak ada yang lupa dan uangnya bisa disiapkan." @retry="load">
    <ul class="ledger card mx-4 mb-8 overflow-hidden md:mx-8">
      <li v-for="l in lists" :key="l.id">
        <RouterLink :to="`/belanja/${l.id}`" class="flex min-h-[72px] items-center justify-between gap-3 px-4 py-3 transition-colors hover:bg-paper">
          <span class="min-w-0">
            <span class="block truncate font-bold">{{ l.judul }}</span>
            <span class="block text-sm text-muted">{{ tanggalPanjang(l.rencana_tanggal) }} · {{ l.jumlah_dibeli }}/{{ l.jumlah_barang }} dibeli</span>
          </span>
          <span class="shrink-0 text-right">
            <span class="amount block font-bold">{{ rp(l.status === 'selesai' ? l.total_dibeli : l.estimasi_total) }}</span>
            <span class="block text-xs font-bold" :class="l.status === 'selesai' ? 'text-masuk' : 'text-muted'">{{ l.status === 'selesai' ? 'Sudah dicatat' : 'Perkiraan' }}</span>
          </span>
        </RouterLink>
      </li>
    </ul>
  </StateView>
</template>
