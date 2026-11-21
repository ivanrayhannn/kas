<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import TxRow from '../components/TxRow.vue'
import { api } from '../lib/api'
import { addDays, isoDate, rp, tanggalPanjang } from '../lib/format'
import type { Transaction } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const PAGE = 50
const q = ref('')
const jenis = ref<'' | 'masuk' | 'keluar'>('')
const periode = ref<'semua' | 'hari' | '7' | 'bulan' | 'pilih'>('semua')
const dari = ref(addDays(isoDate(), -6))
const sampai = ref(isoDate())
const categoryId = ref('')
const items = ref<Transaction[]>([])
const total = ref(0)
const loading = ref(true)
const more = ref(false)
const error = ref<string | null>(null)

const range = computed(() => {
  const t = isoDate()
  if (periode.value === 'hari') return { dari: t, sampai: t }
  if (periode.value === '7') return { dari: addDays(t, -6), sampai: t }
  if (periode.value === 'bulan') return { dari: t.slice(0, 8) + '01', sampai: t }
  if (periode.value === 'pilih') return { dari: dari.value, sampai: sampai.value }
  return {}
})
const filtered = computed(() => !!(q.value.trim() || jenis.value || categoryId.value || periode.value !== 'semua'))
const catOptions = computed(() => s.categories.filter((c) => !jenis.value || c.jenis === jenis.value))

const groups = computed(() => {
  const map = new Map<string, { tanggal: string; items: Transaction[]; masuk: number; keluar: number }>()
  for (const t of items.value) {
    const g = map.get(t.tanggal) ?? { tanggal: t.tanggal, items: [], masuk: 0, keluar: 0 }
    g.items.push(t)
    g[t.jenis] += t.nominal
    map.set(t.tanggal, g)
  }
  return [...map.values()]
})

async function load(append = false) {
  error.value = null
  append ? (more.value = true) : (loading.value = true)
  const p = new URLSearchParams({ limit: String(PAGE), offset: String(append ? items.value.length : 0) })
  if (q.value.trim()) p.set('q', q.value.trim())
  if (jenis.value) p.set('jenis', jenis.value)
  if (categoryId.value) p.set('category_id', categoryId.value)
  const r = range.value
  if (r.dari) p.set('dari', r.dari)
  if (r.sampai) p.set('sampai', r.sampai)
  try {
    const res = await api<{ items: Transaction[]; total: number }>(`/transactions?${p}`)
    items.value = append ? [...items.value, ...res.items] : res.items
    total.value = res.total
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
    more.value = false
  }
}

let timer: number | undefined
watch(q, () => { clearTimeout(timer); timer = window.setTimeout(() => load(), 300) })
watch([jenis, periode, categoryId, dari, sampai], () => load())
watch(jenis, () => { if (!catOptions.value.some((c) => c.id === categoryId.value)) categoryId.value = '' })

function reset() {
  q.value = ''; jenis.value = ''; periode.value = 'semua'; categoryId.value = ''
}

onMounted(async () => {
  if (!s.categories.length) s.loadCategories().catch(() => {})
  load()
})

const periodeOpts = [
  ['semua', 'Semua'], ['hari', 'Hari ini'], ['7', '7 hari'], ['bulan', 'Bulan ini'], ['pilih', 'Pilih tanggal'],
] as const
</script>

<template>
  <PageHeader title="Riwayat" :subtitle="loading ? undefined : `${total} catatan${filtered ? ' sesuai filter' : ''}`" />

  <div class="space-y-3 px-4 pb-4 md:px-8">
    <div class="relative">
      <label for="cari" class="sr-only">Cari catatan atau kategori</label>
      <input id="cari" v-model="q" type="search" class="field pl-4" placeholder="Cari catatan atau kategori" />
    </div>
    <div class="flex flex-wrap gap-2" role="group" aria-label="Jenis">
      <button v-for="[v, l] in [['', 'Semua jenis'], ['masuk', 'Uang Masuk'], ['keluar', 'Uang Keluar']] as const" :key="v"
        type="button" class="chip" :aria-pressed="jenis === v" @click="jenis = v">{{ l }}</button>
    </div>
    <div class="flex flex-wrap gap-2" role="group" aria-label="Periode">
      <button v-for="[v, l] in periodeOpts" :key="v" type="button" class="chip shrink-0" :aria-pressed="periode === v" @click="periode = v">{{ l }}</button>
    </div>
    <div v-if="periode === 'pilih'" class="grid grid-cols-2 gap-3">
      <div><label class="label" for="dari">Dari</label><input id="dari" v-model="dari" type="date" class="field" :max="sampai" /></div>
      <div><label class="label" for="sampai">Sampai</label><input id="sampai" v-model="sampai" type="date" class="field" :min="dari" :max="isoDate()" /></div>
    </div>
    <div>
      <label class="label" for="kategori">Kategori</label>
      <select id="kategori" v-model="categoryId" class="field">
        <option value="">Semua kategori</option>
        <option v-for="c in catOptions" :key="c.id" :value="c.id">{{ c.nama }} ({{ c.jenis === 'masuk' ? 'masuk' : 'keluar' }})</option>
      </select>
    </div>
  </div>

  <StateView :loading="loading" :error="error" :empty="!items.length"
    :empty-title="filtered ? 'Tidak ada catatan yang cocok' : 'Belum ada catatan'"
    :empty-text="filtered ? 'Coba ubah kata kunci atau filter.' : 'Catatan uang masuk dan keluar akan muncul di sini, dari yang terbaru.'"
    @retry="load()">
    <template #empty-action>
      <button v-if="filtered" type="button" class="btn btn-ghost mt-4" @click="reset">Hapus semua filter</button>
      <RouterLink v-else to="/catat" class="btn btn-primary mt-4">Catat transaksi</RouterLink>
    </template>
    <div class="space-y-4 px-4 pb-8 md:px-8">
      <section v-for="g in groups" :key="g.tanggal" class="card overflow-hidden" :aria-label="tanggalPanjang(g.tanggal)">
        <header class="flex flex-wrap items-baseline justify-between gap-x-3 border-b border-line bg-paper/60 px-4 py-2.5 text-sm">
          <h2 class="font-bold">{{ tanggalPanjang(g.tanggal) }}</h2>
          <p class="amount text-muted"><span class="text-masuk">+ {{ rp(g.masuk) }}</span> · <span class="text-keluar">− {{ rp(g.keluar) }}</span></p>
        </header>
        <div class="ledger"><TxRow v-for="t in g.items" :key="t.id" :tx="t" /></div>
      </section>
      <button v-if="items.length < total" type="button" class="btn btn-ghost w-full" :disabled="more" @click="load(true)">
        {{ more ? 'Memuat…' : `Tampilkan lebih banyak (${total - items.length} lagi)` }}
      </button>
    </div>
  </StateView>
</template>
