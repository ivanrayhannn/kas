import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { api, ApiError, hasToken, setToken } from '../lib/api'
import type { Category, Jenis, Store, Summary, Transaction, User } from '../lib/types'

export interface TxBody { jenis: Jenis; nominal: number; category_id: string; tanggal: string; catatan: string | null }
interface Toast { id: number; text: string; tone: 'ok' | 'warn' | 'error' }

const OUTBOX_KEY = 'kas.outbox'
const SESSION_KEY = 'kas.session'
const CATS_KEY = 'kas.categories'
const readJson = <T>(key: string, fallback: T): T => {
  try { return JSON.parse(localStorage.getItem(key) || '') ?? fallback } catch { return fallback }
}
const readOutbox = () => readJson<TxBody[]>(OUTBOX_KEY, [])

export const useApp = defineStore('app', () => {
  const user = ref<User | null>(null)
  const store = ref<Store | null>(null)
  const summary = ref<Summary | null>(null)
  const categories = ref<Category[]>([])
  const toasts = ref<Toast[]>([])
  const outbox = ref<TxBody[]>(readOutbox())
  const ready = ref(false)

  const loggedIn = computed(() => !!user.value)

  // Salinan sesi di ponsel, supaya aplikasi tetap bisa dibuka dan dipakai mencatat saat offline.
  watch([user, store], () => {
    user.value ? localStorage.setItem(SESSION_KEY, JSON.stringify({ user: user.value, store: store.value }))
      : localStorage.removeItem(SESSION_KEY)
  })

  function toast(text: string, tone: Toast['tone'] = 'ok') {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, text, tone })
    setTimeout(() => (toasts.value = toasts.value.filter((t) => t.id !== id)), 3500)
  }

  function setSession(data: { token?: string; user: User; store: Store | null }) {
    if (data.token) setToken(data.token)
    user.value = data.user
    store.value = data.store
  }

  function clearSession() {
    setToken('')
    user.value = null
    store.value = null
    summary.value = null
    categories.value = []
    localStorage.removeItem(CATS_KEY)
  }

  async function boot() {
    if (hasToken()) {
      try {
        setSession(await api('/me'))
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) clearSession()
        else {
          const cached = readJson<{ user: User; store: Store | null } | null>(SESSION_KEY, null)
          if (cached) setSession(cached)
        }
      }
    }
    ready.value = true
  }

  async function logout() {
    try { await api('/auth/logout', { method: 'POST' }) } catch { /* tetap keluar di perangkat ini */ }
    outbox.value = []
    localStorage.removeItem(OUTBOX_KEY)
    clearSession()
  }

  async function loadSummary() {
    summary.value = await api<Summary>('/summary')
    return summary.value
  }

  async function loadCategories() {
    try {
      categories.value = await api<Category[]>('/categories')
      localStorage.setItem(CATS_KEY, JSON.stringify(categories.value))
    } catch (e) {
      const cached = readJson<Category[]>(CATS_KEY, [])
      if (!(e instanceof ApiError && e.status === 0 && cached.length)) throw e
      categories.value = cached
    }
    return categories.value
  }

  function applySummary(s: Summary | undefined) {
    if (!s) return
    const wasLow = summary.value?.kas_menipis
    summary.value = s
    if (s.kas_menipis && !wasLow) toast('Kas menipis. Sisa kas di bawah batas yang Anda atur.', 'warn')
  }

  function saveOutbox() { localStorage.setItem(OUTBOX_KEY, JSON.stringify(outbox.value)) }

  /** Simpan catatan. Tanpa internet, catatan disimpan di ponsel dan dikirim saat online. */
  async function saveTransaction(body: TxBody): Promise<'online' | 'offline'> {
    try {
      const r = await api<{ transaction: Transaction; summary: Summary }>('/transactions', { method: 'POST', body })
      applySummary(r.summary)
      return 'online'
    } catch (e) {
      if (e instanceof ApiError && e.status === 0) {
        outbox.value.push(body)
        saveOutbox()
        return 'offline'
      }
      throw e
    }
  }

  let flushing = false
  async function flushOutbox() {
    if (flushing || !outbox.value.length || !user.value) return
    flushing = true
    let sent = 0
    try {
      while (outbox.value.length) {
        try {
          const r = await api<{ summary: Summary }>('/transactions', { method: 'POST', body: outbox.value[0] })
          applySummary(r.summary)
        } catch (e) {
          if (e instanceof ApiError && e.status === 0) break
          toast(`Satu catatan tertunda ditolak server: ${(e as Error).message}`, 'error')
        }
        outbox.value.shift()
        saveOutbox()
        sent++
      }
    } finally {
      flushing = false
    }
    if (sent && !outbox.value.length) toast(`${sent} catatan tertunda sudah terkirim.`)
  }

  return {
    user, store, summary, categories, toasts, outbox, ready, loggedIn,
    toast, setSession, clearSession, boot, logout, loadSummary, loadCategories, applySummary,
    saveTransaction, flushOutbox,
  }
})
