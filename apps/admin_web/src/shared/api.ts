import { auth } from './firebase'

const BASE = import.meta.env.VITE_GATEWAY_BASE || 'http://localhost:8080'

export async function apiFetch(path: string, init: RequestInit = {}) {
  const user = auth.currentUser
  const token = user ? await user.getIdToken() : undefined
  const headers = new Headers(init.headers || {})
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (!headers.has('Content-Type') && init.body) headers.set('Content-Type','application/json')
  return fetch(`${BASE}${path}`, { ...init, headers })
}
