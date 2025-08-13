import React, { useState, useEffect } from 'react'
import { apiFetch } from '../../shared/api'

export default function PulseBoard() {
  const [recentAnswers, setRecentAnswers] = useState([])
  const [topSources, setTopSources] = useState([])
  const [stats, setStats] = useState({
    totalQueries: 0,
    totalDocuments: 0,
    avgConfidence: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPulseData()
  }, [])

  async function loadPulseData() {
    try {
      setLoading(true)
      
      // Load recent documents (we already have this endpoint)
      const recentResp = await apiFetch('/ingest/recent')
      const recentData = await recentResp.json()
      setTopSources(recentData.items || [])
      
      // Mock data for now - in real implementation, these would be separate endpoints
      setRecentAnswers([
        {
          id: '1',
          question: 'How are we doing on retention?',
          answer: 'Based on Q3 strategy, we need to fix bug X and raise NPS by 5 points.',
          confidence: 0.85,
          timestamp: new Date().toISOString(),
          sources: ['Retention Strategy Q3']
        },
        {
          id: '2', 
          question: 'What are our main priorities?',
          answer: 'Focus on customer satisfaction and product stability improvements.',
          confidence: 0.78,
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          sources: ['Strategic Plan 2024']
        }
      ])
      
      setStats({
        totalQueries: 42,
        totalDocuments: recentData.items?.length || 0,
        avgConfidence: 0.82
      })
      
    } catch (error) {
      console.error('Failed to load pulse data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading pulse data...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">Q</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Queries</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.totalQueries}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">D</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Documents</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.totalDocuments}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-medium">%</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Confidence</dt>
                  <dd className="text-lg font-medium text-gray-900">{Math.round(stats.avgConfidence * 100)}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Answers */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Answers</h3>
          <div className="space-y-4">
            {recentAnswers.map((answer) => (
              <div key={answer.id} className="border-l-4 border-indigo-400 pl-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{answer.question}</p>
                    <p className="mt-1 text-sm text-gray-600">{answer.answer}</p>
                    <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                      <span>Confidence: {Math.round(answer.confidence * 100)}%</span>
                      <span>Sources: {answer.sources.join(', ')}</span>
                      <span>{new Date(answer.timestamp).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Sources */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Sources</h3>
          <div className="space-y-3">
            {topSources.slice(0, 5).map((source) => (
              <div key={source.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{source.title}</p>
                  <p className="text-xs text-gray-500">
                    {source.chunks} chunks • {source.type} • {source.createdAt}
                  </p>
                </div>
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={loadPulseData}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          Refresh Pulse Data
        </button>
      </div>
    </div>
  )
}
