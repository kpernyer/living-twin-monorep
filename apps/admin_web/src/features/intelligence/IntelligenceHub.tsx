import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { Brain, MessageSquare, Target, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { apiFetch } from '../../shared/api'

const IntelligenceHub = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const response = await apiFetch('/intelligence/dashboard')
      const data = await response.json()
      setDashboardData(data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSetupDemo = async () => {
    try {
      await apiFetch('/intelligence/setup-demo', { method: 'POST' })
      await loadDashboardData()
    } catch (error) {
      console.error('Failed to setup demo:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Strategic Intelligence Center</h1>
          <p className="text-muted-foreground">
            Transform market intelligence into strategic insights for organizational alignment
          </p>
        </div>
        <Button onClick={handleSetupDemo} className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Setup Demo
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Strategic Insights</p>
                <p className="text-2xl font-bold">{dashboardData?.total_truths || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Priority Communications</p>
                <p className="text-2xl font-bold">{dashboardData?.queue_length || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">High Impact</p>
                <p className="text-2xl font-bold">
                  {dashboardData?.high_impact_truths?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-purple-500" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending</p>
                <p className="text-2xl font-bold">
                  {dashboardData?.pending_communications?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="truths">Strategic Insights</TabsTrigger>
          <TabsTrigger value="communications">Priority Communications</TabsTrigger>
          <TabsTrigger value="generate">Generate</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <OverviewTab dashboardData={dashboardData} />
        </TabsContent>

        <TabsContent value="truths" className="space-y-4">
          <TruthsTab />
        </TabsContent>

        <TabsContent value="communications" className="space-y-4">
          <CommunicationsTab />
        </TabsContent>

        <TabsContent value="generate" className="space-y-4">
          <GenerateTab onGenerated={loadDashboardData} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Overview Tab Component
const OverviewTab = ({ dashboardData }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Recent Truths */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Recent Strategic Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData?.recent_truths?.map((truth) => (
              <div key={truth.id} className="p-3 border rounded-lg">
                <div className="flex items-start justify-between">
                  <p className="text-sm font-medium">{truth.statement}</p>
                  <Badge variant={getImpactVariant(truth.impact_level)}>{truth.impact_level}</Badge>
                </div>
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <span>Confidence: {(truth.confidence * 100).toFixed(0)}%</span>
                  <span>Evidence: {truth.evidence_count}</span>
                  <span>{truth.category}</span>
                </div>
              </div>
            ))}
            {(!dashboardData?.recent_truths || dashboardData.recent_truths.length === 0) && (
              <p className="text-muted-foreground text-center py-4">No recent strategic insights</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Pending Communications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Pending Priority Communications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData?.pending_communications?.map((comm) => (
              <div key={comm.id} className="p-3 border rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium">{comm.topic}</p>
                    <p className="text-xs text-muted-foreground mt-1">{comm.content}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge variant={getCommunicationVariant(comm.type)}>{comm.type}</Badge>
                    <span className="text-xs text-muted-foreground">
                      Priority: {comm.priority}/10
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {(!dashboardData?.pending_communications ||
              dashboardData.pending_communications.length === 0) && (
              <p className="text-muted-foreground text-center py-4">
                No pending priority communications
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* High Impact Truths */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            High Impact Strategic Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dashboardData?.high_impact_truths?.map((truth) => (
              <div key={truth.id} className="p-4 border rounded-lg bg-orange-50">
                <div className="flex items-start justify-between">
                  <p className="text-sm font-medium text-orange-900">{truth.statement}</p>
                  <Badge variant="destructive">{truth.impact_level}</Badge>
                </div>
                <div className="flex items-center gap-4 mt-2 text-xs text-orange-700">
                  <span>Confidence: {(truth.confidence * 100).toFixed(0)}%</span>
                  <span>Evidence: {truth.evidence_count}</span>
                  <span>{truth.category}</span>
                </div>
              </div>
            ))}
            {(!dashboardData?.high_impact_truths ||
              dashboardData.high_impact_truths.length === 0) && (
              <p className="text-muted-foreground text-center py-4 col-span-2">
                No high impact strategic insights
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Truths Tab Component
const TruthsTab = () => {
  const [truths, setTruths] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTruths()
  }, [])

  const loadTruths = async () => {
    try {
      setLoading(true)
      const response = await apiFetch('/intelligence/truths')
      const data = await response.json()
      setTruths(data)
    } catch (error) {
      console.error('Failed to load truths:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading truths...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Strategic Insights</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {truths.map((truth) => (
            <div key={truth.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium">{truth.statement}</p>
                  <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                    <span>Confidence: {(truth.confidence * 100).toFixed(0)}%</span>
                    <span>Evidence: {truth.evidence_count}</span>
                    <span>Category: {truth.category}</span>
                    <span>Created: {new Date(truth.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <Badge variant={getImpactVariant(truth.impact_level)}>{truth.impact_level}</Badge>
              </div>
            </div>
          ))}
          {truths.length === 0 && (
            <p className="text-muted-foreground text-center py-8">No strategic insights found</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Communications Tab Component
const CommunicationsTab = () => {
  const [communications, setCommunications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCommunications()
  }, [])

  const loadCommunications = async () => {
    try {
      setLoading(true)
      const response = await apiFetch('/intelligence/communications')
      const data = await response.json()
      setCommunications(data)
    } catch (error) {
      console.error('Failed to load communications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAcknowledge = async (communicationId) => {
    try {
      await apiFetch(`/intelligence/communications/${communicationId}/acknowledge`, {
        method: 'POST',
      })
      await loadCommunications()
    } catch (error) {
      console.error('Failed to acknowledge communication:', error)
    }
  }

  if (loading) {
    return <div>Loading communications...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Priority Communications Queue</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {communications.map((comm) => (
            <div key={comm.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="font-medium">{comm.topic}</p>
                    <Badge variant={getCommunicationVariant(comm.type)}>{comm.type}</Badge>
                    {comm.acknowledged && <CheckCircle className="h-4 w-4 text-green-500" />}
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{comm.content}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>Priority: {comm.priority}/10</span>
                    <span>Attempts: {comm.attempts}</span>
                    <span>Scheduled: {new Date(comm.scheduled_for).toLocaleString()}</span>
                  </div>
                </div>
                {!comm.acknowledged && (
                  <Button size="sm" onClick={() => handleAcknowledge(comm.id)}>
                    Acknowledge
                  </Button>
                )}
              </div>
            </div>
          ))}
          {communications.length === 0 && (
            <p className="text-muted-foreground text-center py-8">
              No priority communications found
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Generate Tab Component
const GenerateTab = ({ onGenerated }) => {
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await apiFetch('/intelligence/templates')
      const data = await response.json()
      setTemplates(data)
      if (data.length > 0) {
        setSelectedTemplate(data[0].id)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const handleGenerate = async () => {
    if (!selectedTemplate) return

    try {
      setLoading(true)
      await apiFetch('/intelligence/generate', {
        method: 'POST',
        body: JSON.stringify({
          agent_ids: ['demo_agent_1', 'demo_agent_2'],
          template_id: selectedTemplate,
          analysis_depth: 'weekly',
          variables: {
            industry: 'technology',
            company_size: 'mid-size',
          },
        }),
      })
      onGenerated()
    } catch (error) {
      console.error('Failed to generate intelligence:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Strategic Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Select Template</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full mt-1 p-2 border rounded-md"
            >
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name} - {template.role}
                </option>
              ))}
            </select>
          </div>

          {selectedTemplate && (
            <div className="p-4 border rounded-lg bg-muted">
              <h4 className="font-medium mb-2">Template Details</h4>
              {templates.find((t) => t.id === selectedTemplate) && (
                <div className="text-sm text-muted-foreground">
                  <p>
                    <strong>Description:</strong>{' '}
                    {templates.find((t) => t.id === selectedTemplate).description}
                  </p>
                  <p>
                    <strong>Category:</strong>{' '}
                    {templates.find((t) => t.id === selectedTemplate).category}
                  </p>
                  <p>
                    <strong>Analysis Depth:</strong>{' '}
                    {templates.find((t) => t.id === selectedTemplate).analysis_depth}
                  </p>
                </div>
              )}
            </div>
          )}

          <Button
            onClick={handleGenerate}
            disabled={!selectedTemplate || loading}
            className="w-full"
          >
            {loading ? 'Generating...' : 'Generate Strategic Intelligence'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// Helper functions
const getImpactVariant = (impactLevel) => {
  switch (impactLevel) {
    case 'critical':
      return 'destructive'
    case 'high':
      return 'default'
    case 'medium':
      return 'secondary'
    case 'low':
      return 'outline'
    default:
      return 'outline'
  }
}

const getCommunicationVariant = (type) => {
  switch (type) {
    case 'order':
      return 'destructive'
    case 'recommendation':
      return 'default'
    case 'nudge':
      return 'secondary'
    default:
      return 'outline'
  }
}

export default IntelligenceHub
