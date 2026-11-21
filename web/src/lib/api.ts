export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}

let token = localStorage.getItem('kas.token') || ''
let onUnauthorized = () => {}

export const setToken = (t: string) => {
  token = t
  t ? localStorage.setItem('kas.token', t) : localStorage.removeItem('kas.token')
}
export const hasToken = () => !!token
export const setUnauthorizedHandler = (fn: () => void) => { onUnauthorized = fn }

function pesanError(data: any, status: number) {
  const d = data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d) && d[0]) {
    const msg = String(d[0].msg || '').replace(/^Value error, /, '')
    if (/greater than 0/.test(msg)) return 'Nominal harus lebih dari 0.'
    if (/email/i.test(msg)) return 'Format email belum benar.'
    if (/at least 8/.test(msg)) return 'Kata sandi minimal 8 karakter.'
    if (/at least 1/.test(msg)) return 'Kolom wajib belum diisi.'
    return msg || 'Data belum lengkap.'
  }
  return status >= 500 ? 'Server sedang bermasalah. Coba lagi sebentar.' : 'Permintaan gagal.'
}

export async function api<T = any>(path: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  let res: Response
  try {
    res = await fetch(`/api${path}`, {
      method: opts.method || 'GET',
      headers: {
        'x-timezone': Intl.DateTimeFormat().resolvedOptions().timeZone,
        ...(opts.body !== undefined ? { 'content-type': 'application/json' } : {}),
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    })
  } catch {
    throw new ApiError('Tidak ada koneksi internet.', 0)
  }
  const data = res.headers.get('content-type')?.includes('json') ? await res.json() : null
  if (res.status === 401 && token) onUnauthorized()
  if (!res.ok) throw new ApiError(pesanError(data, res.status), res.status)
  return data as T
}
