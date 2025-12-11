import { useState, useEffect } from 'react'
import { FaArrowUp, FaArrowDown, FaExclamationCircle, FaLightbulb, FaBullseye, FaWallet } from 'react-icons/fa'
import { expenseService } from '../services/api'
import { formatCurrency } from '../utils/currency'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import './Analysis.css'

function Analysis() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadAnalysis()
  }, [])

  const loadAnalysis = async () => {
    try {
      setLoading(true)
      const data = await expenseService.getAnalysis()
      if (data.success) {
        setAnalysis(data.analysis)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const COLORS = [
    '#6366f1',
    '#8b5cf6',
    '#ec4899',
    '#f59e0b',
    '#10b981',
    '#06b6d4',
    '#ef4444',
    '#84cc16',
  ]

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <span>Error loading analysis: {error}</span>
      </div>
    )
  }

  if (!analysis || Object.keys(analysis).length === 0) {
    return (
      <div className="empty-state">
        <FaBullseye size={48} className="empty-state-icon" />
        <p>No analysis data available. Add some expenses to see insights!</p>
      </div>
    )
  }

  // Prepare chart data
  const categoryData = analysis.category_breakdown
    ? Object.entries(analysis.category_breakdown).map(([name, value]) => ({
        name,
        value: parseFloat(value),
      }))
    : []

  const comparison = analysis.comparison || {}
  const trends = analysis.trends || []
  const insights = analysis.insights || []
  const recommendations = analysis.recommendations || []
  const alerts = analysis.overspending_alerts || []

  return (
    <div className="analysis-page">
      <div className="page-header">
        <h1>Spending Analysis</h1>
        <button className="btn btn-secondary" onClick={loadAnalysis}>
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <FaWallet size={24} />
          </div>
          <div className="stat-label">Total Spending</div>
          <div className="stat-value">{formatCurrency(analysis.total_spending || 0)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <FaBullseye size={24} />
          </div>
          <div className="stat-label">Average Expense</div>
          <div className="stat-value">
            {formatCurrency(analysis.average_expense || 0)}
          </div>
        </div>

        {comparison.percent_change !== undefined && (
          <div className="stat-card">
            <div className="stat-icon">
              {comparison.percent_change > 0 ? (
                <FaArrowUp size={24} />
              ) : (
                <FaArrowDown size={24} />
              )}
            </div>
            <div className="stat-label">vs Previous Month</div>
            <div className="stat-value">
              {comparison.percent_change > 0 ? '+' : ''}
              {comparison.percent_change?.toFixed(1)}%
            </div>
            <div
              className={`stat-change ${comparison.percent_change > 0 ? 'negative' : 'positive'}`}
            >
              {comparison.percent_change > 0 ? 'Increased' : 'Decreased'} by{' '}
              {formatCurrency(Math.abs(comparison.total_change || 0))}
            </div>
          </div>
        )}

        <div className="stat-card">
          <div className="stat-icon">
            <FaExclamationCircle size={24} />
          </div>
          <div className="stat-label">Alerts</div>
          <div className="stat-value">{alerts.length}</div>
        </div>
      </div>

      {/* Charts */}
      {categoryData.length > 0 && (
        <div className="charts-grid">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Category Breakdown</h2>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border)',
                    borderRadius: '0.5rem',
                  }}
                  formatter={(value) => formatCurrency(value)}
                />
                <Bar dataKey="value" fill="var(--primary)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Spending Distribution</h2>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <FaExclamationCircle size={20} />
              Overspending Alerts
            </h2>
          </div>
          <div className="alerts-list">
            {alerts.map((alert, index) => (
              <div key={index} className="alert-item alert-error">
                {alert}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <FaLightbulb size={20} />
              Insights
            </h2>
          </div>
          <div className="insights-list">
            {insights.map((insight, index) => (
              <div key={index} className="insight-item">
                <FaLightbulb size={16} />
                <span>{insight}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <FaBullseye size={20} />
              Recommendations
            </h2>
          </div>
          <div className="recommendations-list">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                <FaBullseye size={16} />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Trends */}
      {trends.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <FaArrowUp size={20} />
              Trends
            </h2>
          </div>
          <div className="trends-list">
            {trends.map((trend, index) => (
              <div key={index} className="trend-item">
                <FaArrowUp size={16} />
                <span>{trend}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Analysis

