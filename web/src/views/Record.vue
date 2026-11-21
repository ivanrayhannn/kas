<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { isoDate, rp, tanggalPanjang } from '../lib/format'
import type { Jenis, Summary, Transaction } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const route = useRoute()
const router = useRouter()
const editId = computed(() => (route.params.id as string) || '')

const jenis = ref<Jenis>(route.query.jenis === 'keluar' ? 'keluar' : 'masuk')
const digits = ref('')
const categoryId = ref('')
const catatan = ref('')
const tanggal = ref(isoDate())
const ubahTanggal = ref(false)
const loading = ref(true)
const loadError = ref<string | null>(null)
const locked = ref<Transaction['sumber'] | null>(null)
const busy = ref(false)
const error = ref('')
const saved = ref<{ mode: 'online' | 'offline'; nominal: number; jenis: Jenis } | null>(null)

const nominal = computed(() => Number(digits.value || 0))
const cats = computed(() => s.categories.filter((c) => c.jenis === jenis.value))
const lastKey = (j: Jenis) => `kas.lastCat.${j}`

function pickDefaultCategory() {
  if (cats.value.some((c) => c.id === categoryId.value)) return
  const last = localStorage.getItem(lastKey(jenis.value))
  categoryId.value = cats.value.find((c) => c.id === last)?.id || cats.value[0]?.id || ''
}
watch(jenis, pickDefaultCategory)

async function load() {
  loading.value = true
  loadError.value = null
  try {
    if (!s.categories.length) await s.loadCategories()
    if (editId.value) {
      const t = await api<Transaction>(`/transactions/${editId.value}`)
      if (t.sumber !== 'manual') locked.value = t.sumber
      jenis.value = t.jenis
      digits.value = String(t.nominal)
      categoryId.value = t.category_id
      catatan.value = t.catatan || ''
      tanggal.value = t.tanggal
      ubahTanggal.value = t.tanggal !== isoDate()
    }
    pickDefaultCategory()
  } catch (e) {
    loadError.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function press(k: string) {
  error.value = ''
  if (k === 'hapus') digits.value = digits.value.slice(0, -1)
  else if ((digits.value + k).replace(/^0+/, '').length <= 12) digits.value = (digits.value + k).replace(/^0+/, '')
}

function onKey(e: KeyboardEvent) {
  const el = e.target as HTMLElement
  if (saved.value || el.closest('input, textarea, select')) return
  if (/^\d$/.test(e.key)) press(e.key)
  else if (e.key === 'Backspace') press('hapus')
  else return
  e.preventDefault()
}
onMounted(() => { load(); window.addEventListener('keydown', onKey) })
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

async function save() {
  if (!nominal.value) return (error.value = 'Ketik nominal dulu.')
  if (!categoryId.value) return (error.value = 'Pilih kategori dulu.')
  busy.value = true
  error.value = ''
  const body = { jenis: jenis.value, nominal: nominal.value, category_id: categoryId.value, tanggal: tanggal.value, catatan: catatan.value.trim() || null }
  try {
    localStorage.setItem(lastKey(jenis.value), categoryId.value)
    if (editId.value) {
      const r = await api<{ summary: Summary }>(`/transactions/${editId.value}`, { method: 'PUT', body })
      s.applySummary(r.summary)
      s.toast('Perubahan tersimpan. Sisa kas sudah disesuaikan.')
      router.replace(`/riwayat/${editId.value}`)
    } else {
      const mode = await s.saveTransaction(body)
      saved.value = { mode, nominal: nominal.value, jenis: jenis.value }
    }
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}

function again() {
  saved.value = null
  digits.value = ''
  catatan.value = ''
}

const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '000', '0', 'hapus']
</script>

<template>
  <PageHeader :title="editId ? 'Perbaiki catatan' : 'Catat transaksi'" :back="editId ? `/riwayat/${editId}` : '/'" />

  <StateView :loading="loading" :error="loadError" @retry="load">
    <div v-if="locked" class="mx-4 card p-5 md:mx-8">
      <p class="font-bold">Catatan ini tidak bisa diubah</p>
      <p class="mt-1 text-sm text-muted">Catatan ini dibuat otomatis dari {{ locked === 'qris' ? 'pembayaran QRIS' : 'catatan belanja' }}. Bila salah, hapus catatannya di halaman detail, lalu perbaiki di sumbernya.</p>
      <RouterLink :to="`/riwayat/${editId}`" class="btn btn-ghost mt-4">Kembali ke detail</RouterLink>
    </div>

    <!-- Konfirmasi setelah simpan -->
    <section v-else-if="saved" class="mx-4 md:mx-8" aria-labelledby="tersimpan">
      <div class="card p-6 text-center">
        <span class="mx-auto grid h-12 w-12 place-items-center rounded-full text-2xl font-extrabold"
          :class="saved.jenis === 'masuk' ? 'bg-masuk-soft text-masuk' : 'bg-keluar-soft text-keluar'" aria-hidden="true">✓</span>
        <h2 id="tersimpan" class="mt-3 text-xl font-extrabold">{{ saved.mode === 'online' ? 'Tersimpan' : 'Tersimpan di ponsel' }}</h2>
        <p class="mt-1 text-muted">{{ saved.jenis === 'masuk' ? 'Uang masuk' : 'Uang keluar' }} {{ rp(saved.nominal) }}</p>
        <template v-if="saved.mode === 'online' && s.summary">
          <p class="mt-5 text-sm font-bold text-muted">Sisa kas sekarang</p>
          <p class="amount text-3xl font-extrabold">{{ rp(s.summary.sisa_kas) }}</p>
          <p v-if="s.summary.kas_menipis" class="mt-3 rounded-lg bg-warn-soft p-3 text-sm font-semibold text-warn">Kas Menipis: sisa kas di bawah {{ rp(s.summary.ambang_kas_menipis) }}.</p>
        </template>
        <p v-else class="mt-4 rounded-lg bg-warn-soft p-3 text-sm text-warn">Tidak ada internet. Catatan dikirim otomatis saat online, lalu sisa kas diperbarui.</p>
      </div>
      <div class="mt-4 grid grid-cols-2 gap-3">
        <button type="button" class="btn btn-primary" @click="again">Catat lagi</button>
        <RouterLink to="/" class="btn btn-ghost">Ke beranda</RouterLink>
      </div>
    </section>

    <form v-else class="px-4 pb-8 md:px-8" @submit.prevent="save">
      <p v-if="route.query.pertama" class="mb-4 rounded-xl bg-masuk-soft p-4 text-sm text-masuk">
        <strong>Toko siap.</strong> Catat transaksi pertama: penjualan hari ini atau belanja tadi pagi.
      </p>

      <div class="grid grid-cols-2 gap-2 rounded-xl bg-surface p-1 ring-1 ring-line" role="group" aria-label="Jenis catatan">
        <button type="button" class="min-h-12 rounded-lg font-bold transition-colors" :aria-pressed="jenis === 'masuk'"
          :class="jenis === 'masuk' ? 'bg-masuk text-on-ink' : 'text-muted hover:text-ink'" @click="jenis = 'masuk'">+ Uang Masuk</button>
        <button type="button" class="min-h-12 rounded-lg font-bold transition-colors" :aria-pressed="jenis === 'keluar'"
          :class="jenis === 'keluar' ? 'bg-keluar text-on-ink' : 'text-muted hover:text-ink'" @click="jenis = 'keluar'">− Uang Keluar</button>
      </div>

      <div class="mt-5 text-center" aria-live="polite">
        <p class="text-sm font-semibold text-muted" id="nominal-label">Nominal</p>
        <p class="amount mt-1 whitespace-normal break-all text-[2.5rem] font-extrabold leading-tight"
          :class="nominal ? (jenis === 'masuk' ? 'text-masuk' : 'text-keluar') : 'text-muted'" aria-labelledby="nominal-label">{{ rp(nominal) }}</p>
      </div>

      <fieldset class="mt-5">
        <legend class="label">Kategori</legend>
        <div class="flex flex-wrap gap-2">
          <button v-for="c in cats" :key="c.id" type="button" class="chip" :aria-pressed="categoryId === c.id" @click="categoryId = c.id">{{ c.nama }}</button>
        </div>
      </fieldset>

      <div class="mt-5 grid grid-cols-3 gap-2" role="group" aria-label="Papan angka">
        <button v-for="k in keys" :key="k" type="button"
          class="h-14 rounded-xl bg-surface text-2xl font-bold ring-1 ring-line transition-transform hover:bg-paper active:scale-[0.97]"
          :aria-label="k === 'hapus' ? 'Hapus satu angka' : k" @click="press(k)">
          <span v-if="k === 'hapus'" aria-hidden="true">⌫</span><template v-else>{{ k }}</template>
        </button>
      </div>

      <div class="mt-5 grid gap-4">
        <div>
          <label class="label" for="catatan">Catatan <span class="font-normal text-muted">(boleh kosong)</span></label>
          <input id="catatan" v-model="catatan" class="field" maxlength="200" placeholder="Contoh: nasi goreng 3 porsi" />
        </div>
        <div>
          <div class="flex items-center justify-between">
            <p class="font-semibold">Tanggal: <span class="font-normal">{{ tanggalPanjang(tanggal) }}</span></p>
            <button v-if="!ubahTanggal" type="button" class="min-h-11 px-2 font-semibold underline underline-offset-4" @click="ubahTanggal = true">Ubah tanggal</button>
          </div>
          <template v-if="ubahTanggal">
            <label class="sr-only" for="tanggal">Tanggal transaksi</label>
            <input id="tanggal" v-model="tanggal" class="field mt-2" type="date" :max="isoDate()" required />
          </template>
        </div>
      </div>

      <p v-if="error" class="error-text mt-4" role="alert">{{ error }}</p>
      <button class="btn mt-5 min-h-14 w-full text-lg" :class="jenis === 'masuk' ? 'btn-masuk' : 'btn-keluar'" :disabled="busy || !nominal">
        {{ busy ? 'Menyimpan…' : nominal ? `Simpan ${rp(nominal)}` : 'Ketik nominal dulu' }}
      </button>
    </form>
  </StateView>
</template>
