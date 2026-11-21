import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { registerSW } from 'virtual:pwa-register'
import App from './App.vue'
import { router } from './router'
import { setUnauthorizedHandler } from './lib/api'
import { useApp } from './stores/app'
import './style.css'

const app = createApp(App).use(createPinia())
const s = useApp()
setUnauthorizedHandler(() => {
  s.clearSession()
  router.replace({ name: 'masuk', query: { sesi: 'habis' } })
})
window.addEventListener('online', () => s.flushOutbox())
registerSW({ immediate: true })

s.boot().then(() => {
  app.use(router).mount('#app')
  s.flushOutbox()
})
