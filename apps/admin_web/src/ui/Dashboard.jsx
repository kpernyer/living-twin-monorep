import React, { useState, useEffect } from 'react'
import { useAuth } from '../features/auth/AuthProvider'
import { apiFetch } from '../shared/api'
import PulseBoard from '../features/pulse/PulseBoard'
import IntelligenceHub from '../features/intelligence/IntelligenceHub'
import StrategicAlignmentDashboard from '../features/intelligence/StrategicAlignmentDashboard'

export default function Dashboard() {
  const { user, organization, logout, getUserRole, getTenantId, isOrganizationAdmin } = useAuth()
  const [activeTab, setActiveTab] = useState('ingest')
  const [question, setQuestion] = useState('How are we doing on retention?')
  const [answer, setAnswer] = useState('')
  const [title, setTitle] = useState('Demo Source')
  const [ingestText, setIngestText] = useState('Paste domain knowledge here...')
  const [recent, setRecent] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadTitle, setUploadTitle] = useState('')

  async function askTwin() {
    try {
      const resp = await apiFetch('/query', {
        method: 'POST',
        body: JSON.stringify({ question, k: 5, tenantId: getTenantId() })
      })
      const data = await resp.json()
      setAnswer(resp.ok ? data.answer : `Error ${resp.status}: ${JSON.stringify(data)}`)
    } catch (error) {
      setAnswer(`Error: ${error.message}`)
    }
  }

  async function doIngest() {
    try {
      const resp = await apiFetch('/query/ingest/text', {
        method: 'POST',
        body: JSON.stringify({ title, text: ingestText, tenantId: getTenantId() })
      })
      const data = await resp.json()
      await loadRecent()
      alert(resp.ok ? `Ingested: ${data.chunks} chunks` : 'Ingest failed')
    } catch (error) {
      alert(`Ingest failed: ${error.message}`)
    }
  }

  async function loadRecent() {
    try {
      const resp = await apiFetch('/query/ingest/recent')
      const data = await resp.json()
      setRecent(data.items || [])
    } catch (error) {
      console.error('Failed to load recent items:', error)
    }
  }

  async function debugRag() {
    try {
      const resp = await apiFetch('/query/debug/rag', {
        method: 'POST',
        body: JSON.stringify({ question, k: 5, tenantId: getTenantId() })
      })
      const data = await resp.json()
      setAnswer(JSON.stringify(data, null, 2))
    } catch (error) {
      setAnswer(`Debug error: ${error.message}`)
    }
  }

  async function doFileUpload() {
    if (!selectedFile) {
      alert('Please select a file first')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('title', uploadTitle || selectedFile.name)
    formData.append('tenantId', getTenantId())

    try {
      const resp = await apiFetch('/query/ingest/upload', {
        method: 'POST',
        body: formData
      })
      const data = await resp.json()
      
      if (resp.ok) {
        await loadRecent()
        alert(`File uploaded successfully!\nType: ${data.fileType}\nChunks: ${data.chunks}`)
        setSelectedFile(null)
        setUploadTitle('')
        // Reset file input
        const fileInput = document.getElementById('fileInput')
        if (fileInput) fileInput.value = ''
      } else {
        alert(`Upload failed: ${data.detail || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`Upload failed: ${error.message}`)
    }
  }

  function handleFileSelect(event) {
    const file = event.target.files[0]
    setSelectedFile(file)
    if (file && !uploadTitle) {
      setUploadTitle(file.name.replace(/\.[^/.]+$/, '')) // Remove extension for title
    }
  }

  useEffect(() => { loadRecent() }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {organization ? organization.name : 'Living Twin'} Admin
              </h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>Welcome, {user?.email}</span>
                {organization && (
                  <>
                    <span>•</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {getUserRole()}
                    </span>
                    {organization.adminPortalUrl && (
                      <>
                        <span>•</span>
                        <a 
                          href={organization.adminPortalUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-500"
                        >
                          Organization Portal
                        </a>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {organization && (
                <div className="text-right text-sm">
                  <div className="font-medium text-gray-900">{organization.name}</div>
                  <div className="text-gray-500">{organization.industry} • {organization.size}</div>
                </div>
              )}
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('pulse')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pulse'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Pulse Dashboard
            </button>
            <button
              onClick={() => setActiveTab('intelligence')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'intelligence'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Strategic Intelligence
            </button>
            <button
              onClick={() => setActiveTab('alignment')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'alignment'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Strategic Alignment
            </button>
            <button
              onClick={() => setActiveTab('ingest')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'ingest'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Ingest & Query
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeTab === 'pulse' ? (
            <PulseBoard />
          ) : activeTab === 'intelligence' ? (
            <IntelligenceHub />
          ) : activeTab === 'alignment' ? (
            <StrategicAlignmentDashboard />
          ) : (
            <div className="grid grid-cols-1 gap-6">
            
            {/* Ask the Twin */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Ask the Twin</h3>
                <div className="space-y-4">
                  <input 
                    value={question} 
                    onChange={e => setQuestion(e.target.value)} 
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Enter your question..."
                  />
                  <div className="flex space-x-3">
                    <button 
                      onClick={askTwin}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Ask
                    </button>
                    <button 
                      onClick={debugRag}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Debug RAG
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Ingest Text */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Ingest Domain Knowledge (Text)</h3>
                <div className="space-y-4">
                  <input 
                    value={title} 
                    onChange={e => setTitle(e.target.value)} 
                    placeholder="Title" 
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <textarea 
                    value={ingestText} 
                    onChange={e => setIngestText(e.target.value)} 
                    rows={6} 
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Paste your domain knowledge here..."
                  />
                  <button 
                    onClick={doIngest}
                    className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Ingest
                  </button>
                </div>
              </div>
            </div>

            {/* File Upload */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Upload Documents (PDF, DOCX, TXT)</h3>
                <div className="space-y-4">
                  <input 
                    value={uploadTitle} 
                    onChange={e => setUploadTitle(e.target.value)} 
                    placeholder="Document title (optional)" 
                    className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <input 
                    id="fileInput"
                    type="file" 
                    accept=".pdf,.docx,.doc,.txt,.md" 
                    onChange={handleFileSelect}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                  {selectedFile && (
                    <div className="p-3 bg-gray-50 rounded-md">
                      Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </div>
                  )}
                  <button 
                    onClick={doFileUpload} 
                    disabled={!selectedFile}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Upload Document
                  </button>
                </div>
              </div>
            </div>

            {/* Recently Ingested */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Recently Ingested</h3>
                <ul className="divide-y divide-gray-200">
                  {recent.map((r) => (
                    <li key={r.id} className="py-3">
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{r.title}</p>
                          <p className="text-sm text-gray-500">{r.createdAt} — {r.type}</p>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
                {recent.length === 0 && (
                  <p className="text-gray-500 text-sm">No documents ingested yet.</p>
                )}
              </div>
            </div>

            {/* Answer Display */}
            {answer && (
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Response</h3>
                  <pre className="bg-gray-50 p-4 rounded-md text-sm overflow-auto whitespace-pre-wrap">
                    {answer}
                  </pre>
                </div>
              </div>
            )}

            </div>
          )}
        </div>
      </main>
    </div>
  )
}
