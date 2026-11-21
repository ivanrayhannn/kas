<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthShell from '../components/AuthShell.vue'
import { api } from '../lib/api'
import { useApp } from '../stores/app'

const s = useApp()
const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const error = ref(route.query.sesi === 'habis' ? 'Sesi Anda sudah berakhir. Silakan masuk lagi.' : '')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    s.setSession(await api('/auth/login', { method: 'POST', body: { email: email.value, password: password.value } }))
    router.replace({ name: s.store ? 'beranda' : 'setup' })
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthShell title="Masuk ke kas resto Anda">
    <form class="grid gap-5" novalidate @submit.prevent="submit">
      <div>
        <label class="label" for="email">Email</label>
        <input id="email" v-model="email" class="field" type="email" autocomplete="email" inputmode="email" required />
      </div>
      <div>
        <label class="label" for="password">Kata sandi</label>
        <input id="password" v-model="password" class="field" type="password" autocomplete="current-password" required />
      </div>
      <p v-if="error" class="error-text" role="alert">{{ error }}</p>
      <button class="btn btn-primary" :disabled="busy || !email || !password">{{ busy ? 'Memeriksa…' : 'Masuk' }}</button>
      <RouterLink to="/lupa-sandi" class="min-h-11 text-center font-semibold underline underline-offset-4">Lupa kata sandi?</RouterLink>
    </form>
    <p class="mt-8 text-center text-muted">Belum punya akun?
      <RouterLink to="/daftar" class="font-bold text-ink underline underline-offset-4">Daftar sekarang</RouterLink>
    </p>
  </AuthShell>
</template>
