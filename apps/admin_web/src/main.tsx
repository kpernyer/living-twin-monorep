import React from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from './features/auth/AuthProvider'
import App from './ui/App'
import { initSentry } from './core/error/sentry'
import './index.css'

// Initialize Sentry for error tracking
initSentry()

const rootElement = document.getElementById('root')
if (!rootElement) {
  throw new Error('Root element not found')
}

createRoot(rootElement).render(
  <AuthProvider>
    <App />
  </AuthProvider>,
)
