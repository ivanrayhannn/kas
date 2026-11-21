<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '../components/AuthShell.vue'
import MoneyInput from '../components/MoneyInput.vue'
import { api } from '../lib/api'
import type { Store } from '../lib/types'
import { useApp } from '../stores/app'

const s = useApp()
const router = useRouter()
const nama = ref('')
const modal = ref<number | null>(null)
const ambang = ref<number | null>(null)
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    s.store = await api<Store>('/store', {
      method: 'POST',
      body: { nama_toko: nama.value, modal_awal: modal.value ?? 0, ambang_kas_menipis: ambang.value },
    })
    router.replace({ name: 'catat', query: { pertama: '1' } })
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthShell :title="`Halo, ${s.user?.nama}. Kenalkan resto Anda.`" lead="Tiga isian ini bisa diubah kapan saja di Pengaturan.">
    <form class="grid gap-6" novalidate @submit.prevent="submit">
      <div>
        <label class="label" for="nama">Nama resto</label>
        <input id="nama" v-model="nama" class="field" autocomplete="organization" required />
      </div>
      <div>
        <label class="label" for="modal">Modal awal</label>
        <MoneyInput id="modal" v-model="modal" placeholder="0" describedby="modal-hint" />
        <p id="modal-hint" class="hint">Uang kas yang ada di laci atau rekening resto saat mulai mencatat.</p>
      </div>
      <div>
        <label class="label" for="ambang">Beri peringatan bila kas di bawah</label>
        <MoneyInput id="ambang" v-model="ambang" placeholder="Boleh dikosongkan" describedby="ambang-hint" />
        <p id="ambang-hint" class="hint">Kosongkan untuk memakai batas bawaan: 20% dari modal awal, paling sedikit Rp 500.000.</p>
      </div>
      <p v-if="error" class="error-text" role="alert">{{ error }}</p>
      <button class="btn btn-primary" :disabled="busy || !nama.trim()">{{ busy ? 'Menyimpan…' : 'Simpan dan catat transaksi pertama' }}</button>
    </form>
  </AuthShell>
</template>
