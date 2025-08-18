import React, { useState } from 'react'
import { useAuth } from '../../features/auth/AuthProvider'
import { apiFetch } from '../../shared/api'

export const AskTwinSection: React.FC = () => {
  const { getTenantId } = useAuth()
  const [question, setQuestion] = useState('How are we doing on retention?')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const askTwin = async () => {
    try {
      setLoading(true)
      const resp = await apiFetch('/query', {
        method: 'POST',
        body: JSON.stringify({ question, k: 5, tenantId: getTenantId() }),
      })
      const data = await resp.json()
      setAnswer(resp.ok ? data.answer : `Error ${resp.status}: ${JSON.stringify(data)}`)
    } catch (error) {
      setAnswer(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  const debugRag = async () => {
    try {
      setLoading(true)
      const resp = await apiFetch('/query/debug/rag', {
        method: 'POST',
        body: JSON.stringify({ question, k: 5, tenantId: getTenantId() }),
      })
      const data = await resp.json()
      setAnswer(JSON.stringify(data, null, 2))
    } catch (error) {
      setAnswer(`Debug error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Ask the Twin</h3>
        <div className="space-y-4">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Enter your question..."
          />
          <div className="flex space-x-3">
            <button
              onClick={askTwin}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {loading ? 'Asking...' : 'Ask'}
            </button>
            <button
              onClick={debugRag}
              disabled={loading}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Debug RAG
            </button>
          </div>
        </div>
      </div>
      {answer && (
        <div className="px-4 py-5 sm:p-6 border-t border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-2">Response</h4>
          <pre className="bg-gray-50 p-4 rounded-md text-sm overflow-auto whitespace-pre-wrap">
            {answer}
          </pre>
        </div>
      )}
    </div>
  )
}
