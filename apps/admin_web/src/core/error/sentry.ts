import * as Sentry from '@sentry/react'

// Environment variables
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN || 'https://your-glitchtip-instance.com/1'
const SENTRY_ENVIRONMENT = import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development'
const SENTRY_RELEASE = import.meta.env.VITE_SENTRY_RELEASE || 'react-admin@1.0.0'

/**
 * Initialize Sentry for error tracking and performance monitoring
 */
export function initSentry() {
  Sentry.init({
    // DSN configuration
    dsn: SENTRY_DSN,
    environment: SENTRY_ENVIRONMENT,
    release: SENTRY_RELEASE,

    // Performance monitoring
    tracesSampleRate: 1.0,
    profilesSampleRate: 1.0,

    // Debug configuration
    debug: import.meta.env.DEV,

    // Before send callback to filter sensitive data
    beforeSend(event, hint) {
      // Remove sensitive data from events
      if (event.extra) {
        delete event.extra.password
        delete event.extra.token
        delete event.extra.api_key
        delete event.extra.secret
        delete event.extra.authorization
      }

      // Filter out certain error types in development
      if (import.meta.env.DEV) {
        // Don't send certain errors in development
        if (event.exception?.values?.[0]?.type === 'ChunkLoadError') {
          return null // Don't send chunk load errors in development
        }
      }

      return event
    },

    // Configure breadcrumbs
    beforeBreadcrumb(breadcrumb, hint) {
      // Filter out sensitive breadcrumbs
      if (
        breadcrumb.message?.includes('password') ||
        breadcrumb.message?.includes('token') ||
        breadcrumb.message?.includes('api_key')
      ) {
        return null
      }
      return breadcrumb
    },

    // Enable automatic session tracking
    autoSessionTracking: true,

    // Attach stack traces
    attachStacktrace: true,
  })
}

/**
 * Set user context for better error tracking
 */
export function setUser(user: {
  id: string
  email?: string
  username?: string
  organization?: string
}) {
  Sentry.setUser({
    id: user.id,
    email: user.email,
    username: user.username,
    ip_address: '{{auto}}',
  })

  if (user.organization) {
    Sentry.setTag('organization', user.organization)
  }
}

/**
 * Set organization context
 */
export function setOrganization(organizationId: string) {
  Sentry.setTag('organization_id', organizationId)
}

/**
 * Add custom context data
 */
export function setContext(key: string, value: any) {
  Sentry.setContext(key, value)
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(breadcrumb: {
  message: string
  category?: string
  type?: string
  data?: Record<string, any>
}) {
  Sentry.addBreadcrumb({
    message: breadcrumb.message,
    category: breadcrumb.category,
    type: breadcrumb.type,
    data: breadcrumb.data,
    timestamp: Date.now() / 1000,
  })
}

/**
 * Manually capture an exception
 */
export function captureException(
  exception: Error,
  context?: {
    extras?: Record<string, any>
    tags?: Record<string, string>
    user?: any
  }
) {
  Sentry.withScope((scope) => {
    if (context?.extras) {
      Object.entries(context.extras).forEach(([key, value]) => {
        scope.setExtra(key, value)
      })
    }
    if (context?.tags) {
      Object.entries(context.tags).forEach(([key, value]) => {
        scope.setTag(key, value)
      })
    }
    if (context?.user) {
      scope.setUser(context.user)
    }
    Sentry.captureException(exception)
  })
}

/**
 * Capture a message
 */
export function captureMessage(
  message: string,
  level: Sentry.SeverityLevel = 'info',
  context?: {
    extras?: Record<string, any>
    tags?: Record<string, string>
  }
) {
  Sentry.withScope((scope) => {
    if (context?.extras) {
      Object.entries(context.extras).forEach(([key, value]) => {
        scope.setExtra(key, value)
      })
    }
    if (context?.tags) {
      Object.entries(context.tags).forEach(([key, value]) => {
        scope.setTag(key, value)
      })
    }
    Sentry.captureMessage(message, level)
  })
}

/**
 * Create a performance transaction
 */
export function startTransaction(
  name: string,
  operation: string,
  description?: string
) {
  return Sentry.startTransaction({
    name,
    op: operation,
    description,
  })
}

/**
 * Close Sentry
 */
export function closeSentry() {
  Sentry.close()
}

/**
 * Error boundary component for React
 */
export const SentryErrorBoundary = Sentry.ErrorBoundary

/**
 * Performance monitoring component
 */
export const SentryProfiler = Sentry.Profiler
