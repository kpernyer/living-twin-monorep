import React, { useState, useEffect } from 'react'
import { Card } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'

const StrategicAlignmentDashboard = () => {
  const [scorecard, setScorecard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadStrategicAlignmentScorecard()
  }, [])

  const loadStrategicAlignmentScorecard = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/intelligence/alignment/scorecard')
      if (!response.ok) {
        throw new Error('Failed to load strategic alignment scorecard')
      }
      const data = await response.json()
      setScorecard(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const calculateAlignment = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/intelligence/alignment/calculate', {
        method: 'POST',
      })
      if (!response.ok) {
        throw new Error('Failed to calculate strategic alignment')
      }
      await loadStrategicAlignmentScorecard()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getZoneColor = (zone) => {
    switch (zone) {
      case 'green':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'yellow':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'red':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getZoneIcon = (zone) => {
    switch (zone) {
      case 'green':
        return '✅'
      case 'yellow':
        return '⚠️'
      case 'red':
        return '🚨'
      default:
        return '❓'
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">Loading strategic alignment data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-red-600">Error: {error}</div>
        <Button onClick={loadStrategicAlignmentScorecard} className="mt-2">
          Retry
        </Button>
      </div>
    )
  }

  if (!scorecard) {
    return (
      <div className="p-6">
        <div className="text-center">No strategic alignment data available</div>
        <Button onClick={calculateAlignment} className="mt-2">
          Calculate Strategic Alignment
        </Button>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Strategic Alignment Dashboard</h2>
        <Button onClick={calculateAlignment} disabled={loading}>
          {loading ? 'Calculating...' : 'Recalculate'}
        </Button>
      </div>

      {/* Overall Score Card */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Overall Strategic Alignment</h3>
          <Badge className={getZoneColor(scorecard.alignment_zone)}>
            {getZoneIcon(scorecard.alignment_zone)} {scorecard.alignment_zone.toUpperCase()}
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {scorecard.overall_alignment_score.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Overall Score</div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {scorecard.strategic_velocity.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Strategic Velocity</div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {scorecard.risk_indicators.length}
            </div>
            <div className="text-sm text-gray-600">Risk Indicators</div>
          </div>
        </div>
      </Card>

      {/* Alignment KPIs */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Alignment KPIs</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Strategic Initiative Velocity</span>
              <span className="text-sm font-bold">
                {scorecard.strategic_initiative_velocity.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${scorecard.strategic_initiative_velocity}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Goal Cascade Alignment</span>
              <span className="text-sm font-bold">
                {scorecard.goal_cascade_alignment.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${scorecard.goal_cascade_alignment}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Decision-Strategy Consistency</span>
              <span className="text-sm font-bold">
                {scorecard.decision_strategy_consistency.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full"
                style={{ width: `${scorecard.decision_strategy_consistency}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Resource Allocation Efficiency</span>
              <span className="text-sm font-bold">
                {scorecard.resource_allocation_efficiency.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-600 h-2 rounded-full"
                style={{ width: `${scorecard.resource_allocation_efficiency}%` }}
              ></div>
            </div>
          </div>
        </div>
      </Card>

      {/* Execution KPIs */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Execution KPIs</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Strategic Response Time</span>
              <span className="text-sm font-bold">
                {scorecard.strategic_response_time.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${scorecard.strategic_response_time}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Cross-Functional Alignment</span>
              <span className="text-sm font-bold">
                {scorecard.cross_functional_alignment.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${scorecard.cross_functional_alignment}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Communication Effectiveness</span>
              <span className="text-sm font-bold">
                {scorecard.strategic_communication_effectiveness.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full"
                style={{ width: `${scorecard.strategic_communication_effectiveness}%` }}
              ></div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Adaptation Speed</span>
              <span className="text-sm font-bold">{scorecard.adaptation_speed.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-orange-600 h-2 rounded-full"
                style={{ width: `${scorecard.adaptation_speed}%` }}
              ></div>
            </div>
          </div>
        </div>
      </Card>

      {/* Risk Indicators */}
      {scorecard.risk_indicators.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Risk Indicators</h3>
          <div className="space-y-2">
            {scorecard.risk_indicators.map((risk, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-red-500">⚠️</span>
                <span className="text-sm">{risk}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Priority Interventions */}
      {scorecard.priority_interventions.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Priority Interventions</h3>
          <div className="space-y-2">
            {scorecard.priority_interventions.map((intervention, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-blue-500">🎯</span>
                <span className="text-sm">{intervention}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Measurement Info */}
      <Card className="p-6">
        <div className="text-sm text-gray-600">
          <p>Last measured: {new Date(scorecard.measurement_date).toLocaleString()}</p>
          <p>Trend 30 days: {scorecard.trend_30_days}</p>
          <p>Trend 60 days: {scorecard.trend_60_days}</p>
          <p>Trend 90 days: {scorecard.trend_90_days}</p>
        </div>
      </Card>
    </div>
  )
}

export default StrategicAlignmentDashboard
