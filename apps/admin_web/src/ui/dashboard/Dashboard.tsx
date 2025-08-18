import React, { useState } from 'react'
import { DashboardHeader } from './DashboardHeader'
import { DashboardNavigation } from './DashboardNavigation'
import { AskTwinSection } from './AskTwinSection'
import { IngestTextSection } from './IngestTextSection'
import { FileUploadSection } from './FileUploadSection'
import { RecentlyIngestedSection } from './RecentlyIngestedSection'
import { NotificationContainer } from '../../components/ui/NotificationContainer'
import PulseBoard from '../../features/pulse/PulseBoard'
import IntelligenceHub from '../../features/intelligence/IntelligenceHub'
import StrategicAlignmentDashboard from '../../features/intelligence/StrategicAlignmentDashboard'
import DocumentInjection from '../../features/document_injection/DocumentInjection'

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('document_injection')

  const renderTabContent = () => {
    switch (activeTab) {
      case 'pulse':
        return <PulseBoard />
      case 'intelligence':
        return <IntelligenceHub />
      case 'alignment':
        return <StrategicAlignmentDashboard />
      case 'document_injection':
        return <DocumentInjection />
      case 'ingest':
        return (
          <div className="grid grid-cols-1 gap-6">
            <AskTwinSection />
            <IngestTextSection />
            <FileUploadSection />
            <RecentlyIngestedSection />
          </div>
        )
      default:
        return <DocumentInjection />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />
      <DashboardNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">{renderTabContent()}</div>
      </main>

      {/* Notification Container */}
      <NotificationContainer />
    </div>
  )
}
