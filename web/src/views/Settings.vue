<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import MoneyInput from '../components/MoneyInput.vue'
import PageHeader from '../components/PageHeader.vue'
import StateView from '../components/StateView.vue'
import { api } from '../lib/api'
import { rp } from '../lib/format'
import type { Category, Jenis, Store, User } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const router = useRouter()
const st = s.store!
const toko = ref({ nama_toko: st.nama_toko, alamat: st.alamat || '', telepon: st.telepon || '' })
const modal = ref<number | null>(st.modal_awal)
const ambang = ref<number | null>(st.ambang_kas_menipis)
const savingToko = ref(false)
const savingKas = ref(false)
const qrBusy = ref(false)
const qrError = ref('')
const nama = ref(s.user!.nama)
const savingNama = ref(false)
const askLogout = ref(false)

const catLoading = ref(true)
const catError = ref<string | null>(null)
const newCat = ref<Record<Jenis, string>>({ masuk: '', keluar: '' })
const renaming = ref('')
const renameText = ref('')
const byJenis = computed(() => ({ masuk: s.categories.filter((c) => c.jenis === 'masuk'), keluar: s.categories.filter((c) => c.jenis === 'keluar') }))

async function saveStore(part: 'toko' | 'kas') {
  part === 'toko' ? (savingToko.value = true) : (savingKas.value = true)
  try {
    s.store = await api<Store>('/store', { method: 'PUT', body: { ...toko.value, modal_awal: modal.value ?? 0, ambang_kas_menipis: ambang.value } })
    s.loadSummary().catch(() => {})
    s.toast(part === 'toko' ? 'Profil toko disimpan.' : 'Modal dan batas kas disimpan. Sisa kas dihitung ulang.')
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    savingToko.value = savingKas.value = false
  }
}

function readAsDataUrl(file: Blob) {
  return new Promise<string>((ok, fail) => {
    const r = new FileReader()
    r.onload = () => ok(String(r.result))
    r.onerror = () => fail(r.error)
    r.readAsDataURL(file)
  })
}

async function shrink(file: File): Promise<string> {
  const url = await readAsDataUrl(file)
  if (file.size <= 900_000 && /image\/(png|jpeg|webp)/.test(file.type)) return url
  const img = new Image()
  img.src = url
  await img.decode()
  const scale = Math.min(1, 1000 / Math.max(img.width, img.height))
  const c = document.createElement('canvas')
  c.width = Math.round(img.width * scale)
  c.height = Math.round(img.height * scale)
  c.getContext('2d')!.drawImage(img, 0, 0, c.width, c.height)
  return c.toDataURL('image/png')
}

async function uploadQr(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  qrError.value = ''
  if (!file.type.startsWith('image/')) return (qrError.value = 'Pilih file gambar (foto atau tangkapan layar QR).')
  qrBusy.value = true
  try {
    s.store = await api<Store>('/store/qr', { method: 'PUT', body: { image: await shrink(file) } })
    s.toast('Gambar QR tersimpan.')
  } catch (err) {
    qrError.value = (err as Error).message
  } finally {
    qrBusy.value = false
  }
}

async function removeQr() {
  qrBusy.value = true
  try { s.store = await api<Store>('/store/qr', { method: 'DELETE' }) }
  catch (e) { s.toast((e as Error).message, 'error') }
  finally { qrBusy.value = false }
}

async function loadCats() {
  catLoading.value = true
  catError.value = null
  try { await s.loadCategories() }
  catch (e) { catError.value = (e as Error).message }
  finally { catLoading.value = false }
}

async function addCat(jenis: Jenis) {
  const nama = newCat.value[jenis].trim()
  if (!nama) return
  try {
    s.categories.push(await api<Category>('/categories', { method: 'POST', body: { nama, jenis } }))
    newCat.value[jenis] = ''
  } catch (e) {
    s.toast((e as Error).message, 'error')
  }
}

async function renameCat(c: Category) {
  if (!renameText.value.trim()) return
  try {
    const r = await api<Category>(`/categories/${c.id}`, { method: 'PUT', body: { nama: renameText.value } })
    c.nama = r.nama
    renaming.value = ''
  } catch (e) {
    s.toast((e as Error).message, 'error')
  }
}

async function deleteCat(c: Category) {
  try {
    await api(`/categories/${c.id}`, { method: 'DELETE' })
    s.categories = s.categories.filter((x) => x.id !== c.id)
    s.toast(`Kategori ${c.nama} dihapus.`)
  } catch (e) {
    s.toast((e as Error).message, 'error')
  }
}

async function saveNama() {
  savingNama.value = true
  try {
    s.user = await api<User>('/me', { method: 'PUT', body: { nama: nama.value } })
    s.toast('Nama disimpan.')
  } catch (e) {
    s.toast((e as Error).message, 'error')
  } finally {
    savingNama.value = false
  }
}

async function logout() {
  await s.logout()
  router.replace('/masuk')
}

onMounted(() => {
  loadCats()
  if (location.hash) document.querySelector(location.hash)?.scrollIntoView()
})
</script>

<template>
  <PageHeader title="Pengaturan" back="/lainnya" />
  <div class="space-y-4 px-4 pb-10 md:px-8">
    <form class="card grid gap-4 p-5" @submit.prevent="saveStore('toko')">
      <h2 class="font-bold">Profil toko</h2>
      <div><label class="label" for="s-nama">Nama resto</label><input id="s-nama" v-model="toko.nama_toko" class="field" maxlength="100" required /></div>
      <div><label class="label" for="s-alamat">Alamat <span class="font-normal text-muted">(boleh kosong)</span></label><input id="s-alamat" v-model="toko.alamat" class="field" maxlength="200" /></div>
      <div><label class="label" for="s-telp">Telepon <span class="font-normal text-muted">(boleh kosong)</span></label><input id="s-telp" v-model="toko.telepon" class="field" type="tel" maxlength="30" /></div>
      <button class="btn btn-primary" :disabled="savingToko || !toko.nama_toko.trim()">{{ savingToko ? 'Menyimpan…' : 'Simpan profil' }}</button>
    </form>

    <form id="kas" class="card grid scroll-mt-4 gap-4 p-5" @submit.prevent="saveStore('kas')">
      <h2 class="font-bold">Modal dan peringatan kas</h2>
      <div>
        <label class="label" for="s-modal">Modal awal</label>
        <MoneyInput id="s-modal" v-model="modal" placeholder="0" describedby="s-modal-hint" />
        <p id="s-modal-hint" class="hint">Mengubah modal awal langsung mengubah sisa kas.</p>
      </div>
      <div>
        <label class="label" for="s-ambang">Peringatan Kas Menipis bila di bawah</label>
        <MoneyInput id="s-ambang" v-model="ambang" placeholder="Pakai batas bawaan" describedby="s-ambang-hint" />
        <p id="s-ambang-hint" class="hint">{{ s.store?.ambang_bawaan ? `Sekarang memakai batas bawaan ${rp(s.store.ambang_efektif)} (20% modal, minimal Rp 500.000).` : 'Kosongkan untuk memakai batas bawaan.' }}</p>
      </div>
      <button class="btn btn-primary" :disabled="savingKas">{{ savingKas ? 'Menyimpan…' : 'Simpan modal dan batas' }}</button>
    </form>

    <section id="qr" class="card grid scroll-mt-4 gap-4 p-5" aria-labelledby="qr-h">
      <h2 id="qr-h" class="font-bold">QR pembayaran</h2>
      <img v-if="s.store?.qr_image" :src="s.store.qr_image" alt="QR pembayaran toko" width="200" height="200" class="aspect-square w-48 rounded-lg border border-line bg-white object-contain p-1" />
      <p v-else class="text-sm text-muted">Belum ada gambar QR. Unggah foto atau tangkapan layar QRIS statis dari bank atau e-wallet Anda.</p>
      <p v-if="qrError" class="error-text" role="alert">{{ qrError }}</p>
      <div class="grid gap-2 sm:grid-cols-2">
        <label for="qr-file" class="btn btn-ghost" :class="qrBusy ? 'pointer-events-none opacity-50' : ''">
          {{ qrBusy ? 'Mengunggah…' : s.store?.qr_image ? 'Ganti gambar QR' : 'Unggah gambar QR' }}
        </label>
        <input id="qr-file" type="file" accept="image/*" class="sr-only" :disabled="qrBusy" @change="uploadQr" />
        <button v-if="s.store?.qr_image" type="button" class="btn btn-danger" :disabled="qrBusy" @click="removeQr">Hapus gambar QR</button>
      </div>
    </section>

    <section class="card p-5" aria-labelledby="kat-h">
      <h2 id="kat-h" class="font-bold">Kategori catatan</h2>
      <p class="mt-1 text-sm text-muted">Kategori yang sudah dipakai tidak bisa dihapus, tapi namanya bisa diubah.</p>
      <StateView :loading="catLoading" :error="catError" @retry="loadCats">
        <div class="mt-4 grid gap-6 md:grid-cols-2">
          <div v-for="j in (['masuk', 'keluar'] as const)" :key="j">
            <h3 class="text-sm font-bold" :class="j === 'masuk' ? 'text-masuk' : 'text-keluar'">{{ j === 'masuk' ? 'Uang Masuk' : 'Uang Keluar' }}</h3>
            <ul class="ledger mt-2">
              <li v-for="c in byJenis[j]" :key="c.id" class="py-2">
                <form v-if="renaming === c.id" class="flex gap-2" @submit.prevent="renameCat(c)">
                  <label :for="`r-${c.id}`" class="sr-only">Nama baru untuk {{ c.nama }}</label>
                  <input :id="`r-${c.id}`" v-model="renameText" class="field" maxlength="50" />
                  <button class="btn btn-primary shrink-0 px-3">Simpan</button>
                  <button type="button" class="btn btn-ghost shrink-0 px-3" @click="renaming = ''">Batal</button>
                </form>
                <div v-else class="flex items-center gap-2">
                  <span class="min-w-0 flex-1 truncate font-semibold">{{ c.nama }} <span v-if="c.dipakai" class="font-normal text-muted">· {{ c.dipakai }}x</span></span>
                  <button type="button" class="min-h-11 rounded-lg px-2 text-sm font-semibold underline underline-offset-4 hover:bg-paper" :aria-label="`Ubah nama ${c.nama}`" @click="renaming = c.id; renameText = c.nama">Ubah</button>
                  <button v-if="!c.dipakai" type="button" class="min-h-11 rounded-lg px-2 text-sm font-semibold text-keluar underline underline-offset-4 hover:bg-keluar-soft" :aria-label="`Hapus ${c.nama}`" @click="deleteCat(c)">Hapus</button>
                </div>
              </li>
            </ul>
            <form class="mt-2 flex gap-2" @submit.prevent="addCat(j)">
              <label :for="`new-${j}`" class="sr-only">Kategori baru uang {{ j }}</label>
              <input :id="`new-${j}`" v-model="newCat[j]" class="field" maxlength="50" placeholder="Kategori baru" />
              <button class="btn btn-ghost shrink-0" :disabled="!newCat[j].trim()">Tambah</button>
            </form>
          </div>
        </div>
      </StateView>
    </section>

    <form class="card grid gap-4 p-5" @submit.prevent="saveNama">
      <h2 class="font-bold">Akun</h2>
      <p class="text-sm">Masuk sebagai <strong>{{ s.user?.email }}</strong></p>
      <div><label class="label" for="a-nama">Nama Anda</label><input id="a-nama" v-model="nama" class="field" maxlength="100" required /></div>
      <div class="grid gap-2 sm:grid-cols-2">
        <button class="btn btn-ghost" :disabled="savingNama || !nama.trim()">Simpan nama</button>
        <button type="button" class="btn btn-danger" @click="askLogout = true">Keluar dari akun</button>
      </div>
    </form>
  </div>

  <ConfirmDialog v-model="askLogout" title="Keluar dari akun?" confirm-label="Keluar" @confirm="logout">
    Anda akan keluar di semua perangkat. Data kas tetap aman dan muncul lagi saat Anda masuk.
    <strong v-if="s.outbox.length" class="mt-2 block text-keluar">{{ s.outbox.length }} catatan belum terkirim karena tidak ada internet. Catatan itu akan hilang bila Anda keluar sekarang.</strong>
  </ConfirmDialog>
</template>
