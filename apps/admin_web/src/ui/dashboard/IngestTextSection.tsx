import React, { useState } from 'react'
import { useAuth } from '../../features/auth/AuthProvider'
import { apiFetch } from '../../shared/api'
import { useNotification } from '../../hooks/useNotification'

export const IngestTextSection: React.FC = () => {
  const { getTenantId } = useAuth()
  const { showSuccess, showError } = useNotification()
  const [title, setTitle] = useState('Demo Source')
  const [ingestText, setIngestText] = useState('Paste domain knowledge here...')
  const [loading, setLoading] = useState(false)

  const doIngest = async () => {
    try {
      setLoading(true)
      const resp = await apiFetch('/query/ingest/text', {
        method: 'POST',
        body: JSON.stringify({ title, text: ingestText, tenantId: getTenantId() }),
      })
      const data = await resp.json()
      if (resp.ok) {
        showSuccess('Ingest Successful', `Successfully ingested ${data.chunks} chunks`)
        // Reset form
        setTitle('')
        setIngestText('Paste domain knowledge here...')
      } else {
        showError('Ingest Failed', 'Failed to ingest text content')
      }
    } catch (error) {
      showError(
        'Ingest Failed',
        `Failed to ingest: ${error instanceof Error ? error.message : 'Unknown error'}`,
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Ingest Domain Knowledge (Text)
        </h3>
        <div className="space-y-4">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title"
            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
          <textarea
            value={ingestText}
            onChange={(e) => setIngestText(e.target.value)}
            rows={6}
            className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Paste your domain knowledge here..."
          />
          <button
            onClick={doIngest}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {loading ? 'Ingesting...' : 'Ingest'}
          </button>
        </div>
      </div>
    </div>
  )
}
