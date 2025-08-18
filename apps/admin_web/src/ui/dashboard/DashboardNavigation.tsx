import React from 'react'

interface DashboardNavigationProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export const DashboardNavigation: React.FC<DashboardNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  const tabs = [
    { id: 'pulse', label: 'Pulse Dashboard' },
    { id: 'intelligence', label: 'Strategic Intelligence' },
    { id: 'alignment', label: 'Strategic Alignment' },
    { id: 'ingest', label: 'Ingest & Query' },
    { id: 'document_injection', label: 'Document Injection' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}
