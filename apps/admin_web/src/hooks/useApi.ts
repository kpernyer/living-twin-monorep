import { useState, useCallback } from 'react'
import { apiFetch } from '../shared/api'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (..._args: any[]) => Promise<void>
  reset: () => void
}

export function useApi<T = any>(
  apiCall: (..._args: any[]) => Promise<Response>
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(
    async (..._args: any[]) => {
      setState(prev => ({ ...prev, loading: true, error: null }))
      
      try {
        const response = await apiCall(..._args)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || `HTTP ${response.status}`)
        }
        
        const data = await response.json()
        setState({ data, loading: false, error: null })
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'An error occurred',
        })
      }
    },
    [apiCall]
  )

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return { ...state, execute, reset }
}

// Convenience hook for common API patterns
export function useQuery<T = any>(_endpoint: string) {
  return useApi<T>(() => apiFetch(_endpoint))
}

export function useMutation<T = any>(_endpoint: string) {
  return useApi<T>((_data: any) =>
    apiFetch(_endpoint, {
      method: 'POST',
      body: JSON.stringify(_data),
    })
  )
}
