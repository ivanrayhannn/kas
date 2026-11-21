<script setup lang="ts">
import { ref } from 'vue'
import AuthShell from '../components/AuthShell.vue'
import { api } from '../lib/api'

const email = ref('')
const sent = ref('')
const devUrl = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const r = await api<{ message: string; dev_reset_url?: string }>('/auth/forgot', { method: 'POST', body: { email: email.value } })
    sent.value = r.message
    devUrl.value = r.dev_reset_url ? new URL(r.dev_reset_url).pathname + new URL(r.dev_reset_url).search : ''
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthShell title="Lupa kata sandi" lead="Masukkan email akun Anda. Kami kirim tautan untuk membuat kata sandi baru.">
    <div v-if="sent" class="card p-5" role="status">
      <p class="font-bold">Periksa email Anda</p>
      <p class="mt-1 text-sm text-muted">{{ sent }} Tautan berlaku 1 jam.</p>
      <p v-if="devUrl" class="mt-4 rounded-lg bg-warn-soft p-3 text-sm text-warn">
        Mode uji coba: server email belum dipasang.
        <RouterLink :to="devUrl" class="font-bold underline underline-offset-4">Buka tautan atur ulang</RouterLink>
      </p>
    </div>
    <form v-else class="grid gap-5" novalidate @submit.prevent="submit">
      <div>
        <label class="label" for="email">Email</label>
        <input id="email" v-model="email" class="field" type="email" autocomplete="email" inputmode="email" required />
      </div>
      <p v-if="error" class="error-text" role="alert">{{ error }}</p>
      <button class="btn btn-primary" :disabled="busy || !email">{{ busy ? 'Mengirim…' : 'Kirim tautan' }}</button>
    </form>
    <p class="mt-8 text-center"><RouterLink to="/masuk" class="font-bold underline underline-offset-4">Kembali ke halaman masuk</RouterLink></p>
  </AuthShell>
</template>
