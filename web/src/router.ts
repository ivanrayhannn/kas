import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useApp } from './stores/app'

// meta.public: tanpa akun. meta.bare: tanpa navigasi bawah.
const routes: RouteRecordRaw[] = [
  { path: '/selamat-datang', name: 'welcome', component: () => import('./views/Welcome.vue'), meta: { public: true, title: 'Selamat datang' } },
  { path: '/masuk', name: 'masuk', component: () => import('./views/Login.vue'), meta: { public: true, title: 'Masuk' } },
  { path: '/daftar', name: 'daftar', component: () => import('./views/Register.vue'), meta: { public: true, title: 'Daftar akun' } },
  { path: '/lupa-sandi', name: 'lupa', component: () => import('./views/Forgot.vue'), meta: { public: true, title: 'Lupa kata sandi' } },
  { path: '/atur-ulang-sandi', name: 'reset', component: () => import('./views/Reset.vue'), meta: { public: true, title: 'Kata sandi baru' } },
  { path: '/siapkan-toko', name: 'setup', component: () => import('./views/SetupStore.vue'), meta: { bare: true, noStore: true, title: 'Siapkan toko' } },
  { path: '/', name: 'beranda', component: () => import('./views/Home.vue'), meta: { title: 'Beranda' } },
  { path: '/catat', name: 'catat', component: () => import('./views/Record.vue'), meta: { bare: true, title: 'Catat transaksi' } },
  { path: '/catat/:id', name: 'perbaiki', component: () => import('./views/Record.vue'), meta: { bare: true, title: 'Perbaiki catatan' } },
  { path: '/riwayat', name: 'riwayat', component: () => import('./views/History.vue'), meta: { title: 'Riwayat' } },
  { path: '/riwayat/:id', name: 'detail', component: () => import('./views/TransactionDetail.vue'), meta: { title: 'Detail catatan' } },
  { path: '/laporan', name: 'laporan', component: () => import('./views/Report.vue'), meta: { title: 'Laporan' } },
  { path: '/qris', name: 'qris', component: () => import('./views/Payments.vue'), meta: { title: 'Pembayaran QRIS' } },
  { path: '/qris/tampil', name: 'qr-tampil', component: () => import('./views/QrShow.vue'), meta: { bare: true, title: 'QR Toko' } },
  { path: '/belanja', name: 'belanja', component: () => import('./views/ShoppingLists.vue'), meta: { title: 'Catatan belanja' } },
  { path: '/belanja/:id', name: 'belanja-detail', component: () => import('./views/ShoppingDetail.vue'), meta: { title: 'Daftar belanja' } },
  { path: '/pengaturan', name: 'pengaturan', component: () => import('./views/Settings.vue'), meta: { title: 'Pengaturan' } },
  { path: '/lainnya', name: 'lainnya', component: () => import('./views/More.vue'), meta: { title: 'Menu lainnya' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const s = useApp()
  if (to.meta.public) {
    if (s.loggedIn && to.name !== 'reset') return { name: s.store ? 'beranda' : 'setup' }
    return true
  }
  if (!s.loggedIn) return { name: localStorage.getItem('kas.welcomed') ? 'masuk' : 'welcome' }
  if (!s.store && !to.meta.noStore) return { name: 'setup' }
  if (s.store && to.name === 'setup') return { name: 'beranda' }
  return true
})

router.afterEach((to) => {
  document.title = `${to.meta.title ?? 'Kas Resto'} · Kas Resto`
})
