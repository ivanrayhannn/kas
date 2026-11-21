<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import MoneyInput from '../components/MoneyInput.vue'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { rp, tanggalPanjang } from '../lib/format'
import type { ShoppingItem, ShoppingList, Summary } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const route = useRoute()
const router = useRouter()
const id = route.params.id as string
const list = ref<ShoppingList | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const busy = ref(false)

const blank = () => ({ nama_barang: '', jumlah: 1, satuan: '', estimasi_harga: null as number | null })
const draft = ref(blank())
const editingId = ref('')
const edit = ref(blank())
const formError = ref('')
const categoryId = ref('')
const askDelete = ref(false)
const editHead = ref(false)
const head = ref({ judul: '', rencana_tanggal: '' })

const done = computed(() => list.value?.status === 'selesai')
const keluarCats = computed(() => s.categories.filter((c) => c.jenis === 'keluar'))
const belum = computed(() => list.value?.items?.filter((i) => !i.sudah_dibeli) ?? [])
const sudah = computed(() => list.value?.items?.filter((i) => i.sudah_dibeli) ?? [])

async function load() {
  loading.value = true
  error.value = null
  try {
    const [l] = await Promise.all([api<ShoppingList>(`/shopping-lists/${id}`), s.categories.length ? null : s.loadCategories()])
    list.value = l
    categoryId.value = keluarCats.value.find((c) => c.nama === 'Bahan Baku')?.id || keluarCats.value[0]?.id || ''
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

async function run(fn: () => Promise<ShoppingList>) {
  busy.value = true
  try { list.value = await fn() }
  catch (e) { s.toast((e as Error).message, 'error') }
  finally { busy.value = false }
}

function bodyOf(i: ShoppingItem, patch: Partial<ShoppingItem> = {}) {
  const { id: _, ...rest } = { ...i, ...patch }
  return rest
}

async function addItem() {
  formError.value = ''
  if (!draft.value.nama_barang.trim()) return (formError.value = 'Tulis nama barang.')
  if (!(draft.value.jumlah > 0)) return (formError.value = 'Jumlah harus lebih dari 0.')
  await run(() => api(`/shopping-lists/${id}/items`, { method: 'POST', body: { ...draft.value, estimasi_harga: draft.value.estimasi_harga ?? 0 } }))
  draft.value = blank()
  document.getElementById('nb')?.focus()
}

const toggle = (i: ShoppingItem) => run(() => api(`/shopping-items/${i.id}`, { method: 'PUT', body: bodyOf(i, { sudah_dibeli: !i.sudah_dibeli }) }))
const setActual = (i: ShoppingItem, v: number | null) => run(() => api(`/shopping-items/${i.id}`, { method: 'PUT', body: bodyOf(i, { harga_aktual: v }) }))
const removeItem = (i: ShoppingItem) => run(() => api(`/shopping-items/${i.id}`, { method: 'DELETE' }))

function startEdit(i: ShoppingItem) {
  editingId.value = i.id
  edit.value = { nama_barang: i.nama_barang, jumlah: i.jumlah, satuan: i.satuan || '', estimasi_harga: i.estimasi_harga }
}
async function saveEdit(i: ShoppingItem) {
  if (!edit.value.nama_barang.trim() || !(edit.value.jumlah > 0)) return
  await run(() => api(`/shopping-items/${i.id}`, { method: 'PUT', body: bodyOf(i, { ...edit.value, estimasi_harga: edit.value.estimasi_harga ?? 0 }) }))
  editingId.value = ''
}

async function saveHead() {
  if (!head.value.judul.trim()) return
  await run(() => api(`/shopping-lists/${id}`, { method: 'PUT', body: head.value }))
  editHead.value = false
}

async function convert() {
  busy.value = true
  try {
    const r = await api<{ list: ShoppingList; summary: Summary }>(`/shopping-lists/${id}/convert`, { method: 'POST', body: { category_id: categoryId.value } })
    list.value = r.list
    s.applySummary(r.summary)
    s.toast(`Tersimpan sebagai uang keluar ${rp(r.list.total_dibeli)}.`)
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    busy.value = false
  }
}

async function removeList() {
  busy.value = true
  try {
    await api(`/shopping-lists/${id}`, { method: 'DELETE' })
    s.toast('Daftar belanja dihapus.')
    router.replace('/belanja')
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    busy.value = false
    askDelete.value = false
  }
}
onMounted(load)
const qty = (i: ShoppingItem) => `${new Intl.NumberFormat('id-ID').format(i.jumlah)}${i.satuan ? ' ' + i.satuan : ''}`
</script>

<template>
  <PageHeader :title="list?.judul || 'Daftar belanja'" back="/belanja" :subtitle="list ? `Rencana ${tanggalPanjang(list.rencana_tanggal).toLowerCase()}` : undefined">
    <button v-if="list && !done && !editHead" type="button" class="btn btn-ghost min-h-11 px-3"
      @click="editHead = true; head = { judul: list.judul, rencana_tanggal: list.rencana_tanggal }">Ubah</button>
  </PageHeader>

  <StateView :loading="loading" :error="error" @retry="load">
    <div v-if="list" class="space-y-4 px-4 pb-8 md:px-8">
      <form v-if="editHead" class="card grid gap-4 p-5" @submit.prevent="saveHead">
        <div><label class="label" for="h-judul">Nama daftar</label><input id="h-judul" v-model="head.judul" class="field" maxlength="100" required /></div>
        <div><label class="label" for="h-tgl">Rencana belanja</label><input id="h-tgl" v-model="head.rencana_tanggal" type="date" class="field" required /></div>
        <div class="grid grid-cols-2 gap-2">
          <button type="button" class="btn btn-ghost" @click="editHead = false">Batal</button>
          <button class="btn btn-primary" :disabled="busy">Simpan</button>
        </div>
      </form>

      <section class="card grid grid-cols-2 gap-4 p-5" aria-label="Total belanja">
        <div><p class="text-sm text-muted">Perkiraan biaya</p><p class="amount text-2xl font-extrabold">{{ rp(list.estimasi_total) }}</p></div>
        <div><p class="text-sm text-muted">Sudah dibeli ({{ list.jumlah_dibeli }}/{{ list.jumlah_barang }})</p><p class="amount text-2xl font-extrabold">{{ rp(list.total_dibeli) }}</p></div>
      </section>

      <p v-if="done" class="rounded-xl bg-masuk-soft p-4 text-sm text-masuk">
        <strong>Sudah dicatat sebagai uang keluar.</strong> Daftar ini tidak bisa diubah lagi.
        <RouterLink v-if="list.transaction_id" :to="`/riwayat/${list.transaction_id}`" class="font-bold underline underline-offset-4">Lihat catatan</RouterLink>
      </p>

      <StateView :empty="!list.items?.length" empty-title="Daftar masih kosong" empty-text="Tambahkan barang pertama di formulir di bawah." />

      <section v-for="[group, label] in [[belum, 'Belum dibeli'], [sudah, 'Sudah dibeli']] as const" v-show="group.length" :key="label" class="card overflow-hidden" :aria-label="label">
        <h2 class="border-b border-line px-4 py-2.5 text-sm font-bold text-muted">{{ label }} ({{ group.length }})</h2>
        <ul class="ledger">
          <li v-for="i in group" :key="i.id" class="px-4 py-3">
            <form v-if="editingId === i.id" class="grid gap-3" @submit.prevent="saveEdit(i)">
              <div><label class="label" :for="`e-n-${i.id}`">Nama barang</label><input :id="`e-n-${i.id}`" v-model="edit.nama_barang" class="field" required /></div>
              <div class="grid grid-cols-2 gap-3">
                <div><label class="label" :for="`e-j-${i.id}`">Jumlah</label><input :id="`e-j-${i.id}`" v-model.number="edit.jumlah" type="number" min="0.01" step="any" class="field" inputmode="decimal" /></div>
                <div><label class="label" :for="`e-s-${i.id}`">Satuan</label><input :id="`e-s-${i.id}`" v-model="edit.satuan" class="field" maxlength="20" /></div>
              </div>
              <div><label class="label" :for="`e-h-${i.id}`">Perkiraan harga (total)</label><MoneyInput :id="`e-h-${i.id}`" v-model="edit.estimasi_harga" placeholder="0" /></div>
              <div class="grid grid-cols-3 gap-2">
                <button type="button" class="btn btn-danger" @click="removeItem(i)">Hapus</button>
                <button type="button" class="btn btn-ghost" @click="editingId = ''">Batal</button>
                <button class="btn btn-primary" :disabled="busy">Simpan</button>
              </div>
            </form>
            <template v-else>
              <div class="flex items-center gap-3">
                <label class="flex min-h-11 min-w-0 flex-1 items-center gap-3">
                  <input type="checkbox" class="h-6 w-6 shrink-0 accent-[var(--masuk)]" :checked="i.sudah_dibeli" :disabled="done || busy" @change="toggle(i)" />
                  <span class="min-w-0">
                    <span class="block font-semibold" :class="i.sudah_dibeli ? 'text-muted line-through' : ''">{{ i.nama_barang }}</span>
                    <span class="block text-sm text-muted">{{ qty(i) }} · perkiraan {{ rp(i.estimasi_harga) }}</span>
                  </span>
                </label>
                <button v-if="!done" type="button" class="min-h-11 shrink-0 rounded-lg px-3 font-semibold underline underline-offset-4 hover:bg-paper" :aria-label="`Ubah ${i.nama_barang}`" @click="startEdit(i)">Ubah</button>
              </div>
              <div v-if="i.sudah_dibeli" class="mt-2 pl-9">
                <label class="label" :for="`a-${i.id}`">Harga sebenarnya</label>
                <MoneyInput v-if="!done" :id="`a-${i.id}`" :model-value="i.harga_aktual" placeholder="Sama dengan perkiraan"
                  @update:model-value="(v) => (i.harga_aktual = v)" @change="setActual(i, i.harga_aktual)" />
                <p v-else :id="`a-${i.id}`" class="amount font-bold">{{ rp(i.harga_aktual ?? i.estimasi_harga) }}</p>
              </div>
            </template>
          </li>
        </ul>
      </section>

      <form v-if="!done" class="card grid gap-3 p-5" novalidate @submit.prevent="addItem">
        <h2 class="font-bold">Tambah barang</h2>
        <div><label class="label" for="nb">Nama barang</label><input id="nb" v-model="draft.nama_barang" class="field" maxlength="100" placeholder="Contoh: cabai merah" /></div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="label" for="jb">Jumlah</label><input id="jb" v-model.number="draft.jumlah" type="number" min="0.01" step="any" class="field" inputmode="decimal" /></div>
          <div><label class="label" for="sb">Satuan</label><input id="sb" v-model="draft.satuan" class="field" maxlength="20" placeholder="kg, ikat, liter" list="satuan" /></div>
        </div>
        <datalist id="satuan"><option v-for="u in ['kg', 'gram', 'liter', 'pcs', 'ikat', 'bungkus', 'karung', 'dus']" :key="u" :value="u" /></datalist>
        <div>
          <label class="label" for="hb">Perkiraan harga (total)</label>
          <MoneyInput id="hb" v-model="draft.estimasi_harga" placeholder="0" describedby="hb-hint" />
          <p id="hb-hint" class="hint">Total untuk barang ini, bukan harga per satuan.</p>
        </div>
        <p v-if="formError" class="error-text" role="alert">{{ formError }}</p>
        <button class="btn btn-ghost" :disabled="busy">Tambah ke daftar</button>
      </form>

      <section v-if="!done" class="card grid gap-3 p-5" aria-labelledby="jadikan">
        <h2 id="jadikan" class="font-bold">Selesai belanja?</h2>
        <p class="text-sm text-muted">Barang yang dicentang dijumlah ({{ rp(list.total_dibeli) }}) lalu dicatat sebagai satu uang keluar. Barang yang belum dicentang tidak ikut.</p>
        <div><label class="label" for="cat">Kategori uang keluar</label>
          <select id="cat" v-model="categoryId" class="field"><option v-for="c in keluarCats" :key="c.id" :value="c.id">{{ c.nama }}</option></select></div>
        <button type="button" class="btn btn-keluar" :disabled="busy || !list.jumlah_dibeli || !list.total_dibeli" @click="convert">Jadikan catatan pengeluaran</button>
        <p v-if="!list.jumlah_dibeli" class="hint">Centang dulu barang yang sudah dibeli.</p>
      </section>

      <button type="button" class="btn btn-danger w-full" @click="askDelete = true">Hapus daftar ini</button>
    </div>
  </StateView>

  <ConfirmDialog v-model="askDelete" title="Hapus daftar belanja?" confirm-label="Ya, hapus" danger :busy="busy" @confirm="removeList">
    {{ done ? 'Catatan uang keluar yang sudah dibuat tetap ada di riwayat.' : 'Semua barang di daftar ini ikut terhapus.' }}
  </ConfirmDialog>
</template>
