import { initializeApp } from 'firebase/app'
import { getAuth, connectAuthEmulator } from 'firebase/auth'

const app = initializeApp({
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
})

export const auth = getAuth(app)

// Auto-connect to emulator if host is provided
if (import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_HOST) {
  const host = import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_HOST
  const url = host.startsWith('http') ? host : `http://${host}`
  try { connectAuthEmulator(auth, url) } catch {}
}
