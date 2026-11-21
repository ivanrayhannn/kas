<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthShell from '../components/AuthShell.vue'
import { api } from '../lib/api'
import { useApp } from '../stores/app'

const route = useRoute()
const router = useRouter()
const s = useApp()
const password = ref('')
const error = ref('')
const busy = ref(false)
const token = String(route.query.token || '')

async function submit() {
  error.value = ''
  if (password.value.length < 8) return (error.value = 'Kata sandi minimal 8 karakter.')
  busy.value = true
  try {
    await api('/auth/reset', { method: 'POST', body: { token, password: password.value } })
    s.clearSession()
    s.toast('Kata sandi baru sudah disimpan. Silakan masuk.')
    router.replace({ name: 'masuk' })
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthShell title="Buat kata sandi baru">
    <p v-if="!token" class="error-text" role="alert">Tautan tidak lengkap. Minta tautan baru di halaman Lupa kata sandi.</p>
    <form v-else class="grid gap-5" novalidate @submit.prevent="submit">
      <div>
        <label class="label" for="password">Kata sandi baru</label>
        <input id="password" v-model="password" class="field" type="password" autocomplete="new-password" aria-describedby="pw-hint" required />
        <p id="pw-hint" class="hint">Minimal 8 karakter. Semua perangkat lain akan otomatis keluar.</p>
      </div>
      <p v-if="error" class="error-text" role="alert">{{ error }}
        <RouterLink v-if="/berlaku/.test(error)" to="/lupa-sandi" class="underline underline-offset-4">Minta tautan baru</RouterLink>
      </p>
      <button class="btn btn-primary" :disabled="busy || !password">{{ busy ? 'Menyimpan…' : 'Simpan kata sandi' }}</button>
    </form>
  </AuthShell>
</template>
