<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '../components/AuthShell.vue'
import { api } from '../lib/api'
import { useApp } from '../stores/app'

const s = useApp()
const router = useRouter()
const form = ref({ nama: '', email: '', password: '' })
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  if (form.value.password.length < 8) return (error.value = 'Kata sandi minimal 8 karakter.')
  busy.value = true
  try {
    s.setSession(await api('/auth/register', { method: 'POST', body: form.value }))
    router.replace({ name: 'setup' })
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthShell title="Buat akun" lead="Satu akun untuk satu resto. Data kas hanya bisa dibuka oleh Anda.">
    <form class="grid gap-5" novalidate @submit.prevent="submit">
      <div>
        <label class="label" for="nama">Nama Anda</label>
        <input id="nama" v-model="form.nama" class="field" autocomplete="name" required />
      </div>
      <div>
        <label class="label" for="email">Email</label>
        <input id="email" v-model="form.email" class="field" type="email" autocomplete="email" inputmode="email" required />
      </div>
      <div>
        <label class="label" for="password">Kata sandi</label>
        <input id="password" v-model="form.password" class="field" type="password" autocomplete="new-password" aria-describedby="pw-hint" required />
        <p id="pw-hint" class="hint">Minimal 8 karakter.</p>
      </div>
      <p v-if="error" class="error-text" role="alert">{{ error }}</p>
      <button class="btn btn-primary" :disabled="busy || !form.nama || !form.email || !form.password">{{ busy ? 'Membuat akun…' : 'Buat akun' }}</button>
    </form>
    <p class="mt-8 text-center text-muted">Sudah punya akun?
      <RouterLink to="/masuk" class="font-bold text-ink underline underline-offset-4">Masuk</RouterLink>
    </p>
  </AuthShell>
</template>
