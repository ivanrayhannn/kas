<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './components/Icon.vue'
import { useApp } from './stores/app'

const route = useRoute()
const s = useApp()
const showNav = computed(() => s.loggedIn && s.store && !route.meta.public && !route.meta.bare)

const mobileNav = [
  { to: '/', label: 'Beranda', icon: 'home' },
  { to: '/riwayat', label: 'Riwayat', icon: 'list' },
  { to: '/catat', label: 'Catat', icon: 'plus' },
  { to: '/laporan', label: 'Laporan', icon: 'chart' },
  { to: '/lainnya', label: 'Lainnya', icon: 'menu' },
] as const
const sideNav = [
  { to: '/', label: 'Beranda', icon: 'home' },
  { to: '/riwayat', label: 'Riwayat', icon: 'list' },
  { to: '/laporan', label: 'Laporan', icon: 'chart' },
  { to: '/qris', label: 'Pembayaran QRIS', icon: 'qr' },
  { to: '/belanja', label: 'Catatan belanja', icon: 'cart' },
  { to: '/pengaturan', label: 'Pengaturan', icon: 'gear' },
] as const

const active = (to: string) => (to === '/' ? route.path === '/' : route.path.startsWith(to))
const moreActive = computed(() => ['/lainnya', '/qris', '/belanja', '/pengaturan'].some((p) => route.path.startsWith(p)))
</script>

<template>
  <a href="#isi" class="sr-only-focusable fixed left-3 top-3 z-50 rounded-lg bg-ink px-4 py-3 font-bold text-on-ink">Lewati ke isi</a>

  <div :class="showNav ? 'md:grid md:grid-cols-[240px_1fr]' : ''" class="min-h-dvh">
    <aside v-if="showNav" class="no-print sticky top-0 hidden h-dvh flex-col border-r border-line bg-surface px-4 py-6 md:flex">
      <p class="px-3 text-lg font-extrabold tracking-tight">{{ s.store?.nama_toko }}</p>
      <p class="px-3 text-sm text-muted">Kas Resto</p>
      <RouterLink to="/catat" class="btn btn-primary mt-6 w-full"><Icon name="plus" /> Catat transaksi</RouterLink>
      <nav aria-label="Menu utama" class="mt-6 flex flex-col gap-1">
        <RouterLink v-for="n in sideNav" :key="n.to" :to="n.to"
          :aria-current="active(n.to) ? 'page' : undefined"
          class="flex min-h-11 items-center gap-3 rounded-lg px-3 font-semibold text-muted transition-colors hover:bg-paper hover:text-ink aria-[current=page]:bg-paper aria-[current=page]:text-ink">
          <Icon :name="n.icon" /> {{ n.label }}
          <span v-if="n.to === '/qris' && s.summary?.pembayaran_menunggu"
            class="ml-auto rounded-md bg-warn-soft px-2 text-sm font-bold text-warn">{{ s.summary.pembayaran_menunggu }}</span>
        </RouterLink>
      </nav>
    </aside>

    <main id="isi" tabindex="-1" class="mx-auto w-full max-w-3xl outline-none"
      :class="showNav ? 'pb-[calc(84px+env(safe-area-inset-bottom))] md:pb-10' : ''">
      <RouterView />
    </main>
  </div>

  <nav v-if="showNav" aria-label="Menu utama"
    class="no-print fixed inset-x-0 bottom-0 z-30 border-t border-line bg-surface pb-[env(safe-area-inset-bottom)] md:hidden">
    <ul class="grid grid-cols-5">
      <li v-for="n in mobileNav" :key="n.to">
        <RouterLink :to="n.to"
          :aria-current="(n.to === '/lainnya' ? moreActive : active(n.to)) ? 'page' : undefined"
          class="flex h-[68px] flex-col items-center justify-center gap-1 text-xs font-semibold text-muted aria-[current=page]:text-ink">
          <span v-if="n.to === '/catat'" class="grid h-11 w-11 place-items-center rounded-xl bg-ink text-on-ink"><Icon name="plus" /></span>
          <Icon v-else :name="n.icon" />
          <span :class="n.to === '/catat' ? 'sr-only' : ''">{{ n.label }}</span>
        </RouterLink>
      </li>
    </ul>
  </nav>

  <div aria-live="polite" class="pointer-events-none fixed inset-x-0 top-3 z-50 flex flex-col items-center gap-2 px-4">
    <p v-for="t in s.toasts" :key="t.id" role="status"
      class="pointer-events-auto max-w-md rounded-xl px-4 py-3 text-sm font-semibold shadow-lg"
      :class="t.tone === 'ok' ? 'bg-ink text-on-ink' : t.tone === 'warn' ? 'bg-warn-soft text-warn border border-warn/30' : 'bg-keluar text-on-ink'">
      {{ t.text }}
    </p>
  </div>
</template>
