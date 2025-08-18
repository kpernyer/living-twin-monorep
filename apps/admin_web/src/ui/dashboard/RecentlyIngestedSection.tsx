import React, { useState, useEffect } from 'react'
import { apiFetch } from '../../shared/api'

interface RecentItem {
  id: string
  title: string
  createdAt: string
  type: string
}

export const RecentlyIngestedSection: React.FC = () => {
  const [recent, setRecent] = useState<RecentItem[]>([])
  const [loading, setLoading] = useState(true)

  const loadRecent = async () => {
    try {
      setLoading(true)
      const resp = await apiFetch('/query/ingest/recent')
      const data = await resp.json()
      setRecent(data.items || [])
    } catch (error) {
      console.error('Failed to load recent items:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRecent()
  }, [])

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recently Ingested</h3>
          <button
            onClick={loadRecent}
            disabled={loading}
            className="text-sm text-indigo-600 hover:text-indigo-500 disabled:text-gray-400"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        {loading ? (
          <div className="text-center py-4">
            <div className="text-gray-500">Loading recent items...</div>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {recent.map((r) => (
              <li key={r.id} className="py-3">
                <div className="flex items-center space-x-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{r.title}</p>
                    <p className="text-sm text-gray-500">
                      {r.createdAt} — {r.type}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
        {!loading && recent.length === 0 && (
          <p className="text-gray-500 text-sm">No documents ingested yet.</p>
        )}
      </div>
    </div>
  )
}
