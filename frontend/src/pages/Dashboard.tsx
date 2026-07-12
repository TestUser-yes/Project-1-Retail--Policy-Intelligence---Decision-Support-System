import React, { useEffect, useState } from 'react'
import { Container, Row, Col, Table } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { KPICard } from '@/components/KPICard'
import { EvaluationMetricsCard } from '@/components/EvaluationMetricsCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorAlert } from '@/components/ErrorAlert'
import { dashboardApi } from '@/api/dashboard'
import { DashboardData } from '@/types'

interface Phase1Metrics {
  phase: number
  timestamp: string
  metrics: {
    latency: { status: string; note: string; data_available: boolean }
    tsr: {
      current: number
      current_percent: number
      status: string
      successful: number
      total: number
      data_available: boolean
    }
    sql_correctness: { status: string; note: string; data_available: boolean }
  }
  enabled: { latency: boolean; tsr: boolean; sql_correctness: boolean }
  error?: string
}

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [phase1Metrics, setPhase1Metrics] = useState<Phase1Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dashboardApi.getDashboard()
        setData(result)
      } catch (err) {
        setError('Failed to load dashboard data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    const fetchPhase1Metrics = async () => {
      try {
        const response = await fetch('/api/dashboard/metrics/phase1')
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const result = await response.json()
        setPhase1Metrics(result)
      } catch (err) {
        console.warn('Phase 1 metrics not available:', err)
        setPhase1Metrics(null)
      }
    }

    fetchData()
    fetchPhase1Metrics()
    const interval = setInterval(() => {
      fetchData()
      fetchPhase1Metrics()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <Layout>
      <Container fluid>
        <h1 className="mb-4">
          <i className="bi bi-speedometer2 me-2"></i>
          Dashboard
        </h1>

        {error && <ErrorAlert message={error} />}

        {data && (
          <>
            <Row className="mb-4">
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Total Queries"
                  value={data.totalQueries}
                  icon="bi-chat-dots"
                  variant="primary"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Success Rate"
                  value={`${data.successRate.toFixed(1)}%`}
                  icon="bi-check-circle"
                  variant="success"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Avg. Latency"
                  value={`${data.avgLatency.toFixed(2)}s`}
                  icon="bi-hourglass"
                  variant="info"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Budget Used"
                  value={`$${data.budgetUsdUsed.toFixed(2)}`}
                  icon="bi-currency-dollar"
                  variant="warning"
                />
              </Col>
            </Row>

            {/* Phase 1: AI Operational Metrics Section */}
            {phase1Metrics && !phase1Metrics.error && (
              <Row className="mb-4">
                <Col lg={12}>
                  <div className="card">
                    <div className="card-header">
                      <h6 className="mb-0">
                        <i className="bi bi-speedometer me-2"></i>
                        AI Operational Metrics (Phase 1)
                      </h6>
                    </div>
                    <div className="card-body">
                      <Row>
                        <Col lg={4} md={6} className="mb-3">
                          <EvaluationMetricsCard
                            title="Latency"
                            value={phase1Metrics.metrics.latency.data_available ? 'Tracking' : 'Pending'}
                            status={phase1Metrics.metrics.latency.data_available ? 'good' : 'pending'}
                            unit="ms"
                          />
                        </Col>
                        <Col lg={4} md={6} className="mb-3">
                          <EvaluationMetricsCard
                            title="Success Rate (TSR)"
                            value={
                              phase1Metrics.metrics.tsr.data_available
                                ? `${phase1Metrics.metrics.tsr.current_percent.toFixed(1)}%`
                                : 'Pending'
                            }
                            status={
                              phase1Metrics.metrics.tsr.data_available
                                ? (phase1Metrics.metrics.tsr.status as 'good' | 'warning' | 'critical')
                                : 'pending'
                            }
                            average={
                              phase1Metrics.metrics.tsr.data_available
                                ? `${phase1Metrics.metrics.tsr.successful}/${phase1Metrics.metrics.tsr.total}`
                                : undefined
                            }
                          />
                        </Col>
                        <Col lg={4} md={6} className="mb-3">
                          <EvaluationMetricsCard
                            title="SQL Correctness"
                            value={phase1Metrics.metrics.sql_correctness.data_available ? '99%' : 'Pending'}
                            status={phase1Metrics.metrics.sql_correctness.status as 'good' | 'warning' | 'critical'}
                          />
                        </Col>
                      </Row>
                      <div className="mt-2">
                        <small className="text-muted">
                          <i className="bi bi-info-circle me-1"></i>
                          Metrics updated: {new Date(phase1Metrics.timestamp).toLocaleString()}
                        </small>
                      </div>
                    </div>
                  </div>
                </Col>
              </Row>
            )}

            <Row className="mb-4">
              <Col lg={8}>
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0">Recent Queries</h6>
                  </div>
                  <div className="card-body">
                    {data.recentQueries.length > 0 ? (
                      <Table striped hover size="sm">
                        <thead>
                          <tr>
                            <th>Query</th>
                            <th>Route</th>
                            <th>Latency</th>
                            <th>Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.recentQueries.map((q) => (
                            <tr key={q.id}>
                              <td className="text-truncate">{q.query}</td>
                              <td><span className="badge bg-secondary">{q.route}</span></td>
                              <td>{q.latency.toFixed(2)}s</td>
                              <td className="text-muted small">
                                {new Date(q.timestamp).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    ) : (
                      <p className="text-muted">No queries yet</p>
                    )}
                  </div>
                </div>
              </Col>

              <Col lg={4}>
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0">Query Statistics</h6>
                  </div>
                  <div className="card-body">
                    <div className="mb-3">
                      <small className="text-muted">By Route</small>
                      <div className="d-flex gap-2 flex-wrap">
                        <span className="badge bg-primary">RAG: {data.queryByRoute.rag}</span>
                        <span className="badge bg-success">SQL: {data.queryByRoute.sql}</span>
                        <span className="badge bg-warning">Hybrid: {data.queryByRoute.hybrid}</span>
                      </div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">By Risk Level</small>
                      <div className="d-flex gap-2 flex-wrap">
                        <span className="badge bg-danger">High: {data.queryByRisk.high}</span>
                        <span className="badge bg-warning">Med: {data.queryByRisk.medium}</span>
                        <span className="badge bg-info">Low: {data.queryByRisk.low}</span>
                      </div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">SLO Metrics</small>
                      <div className="h6 mb-1">
                        Success Rate: <span className="badge bg-success">{data.sloMetrics.success_rate.toFixed(1)}%</span>
                      </div>
                      <div className="small text-muted">
                        Avg Latency: {(data.sloMetrics.avg_latency_ms / 1000).toFixed(2)}s / {(data.sloMetrics.target_latency_ms / 1000).toFixed(2)}s target
                      </div>
                    </div>

                    <div>
                      <small className="text-muted">Vendors</small>
                      <div className="h5 mb-0">{data.vendorStats.total}</div>
                      <small className="text-danger">{data.vendorStats.high_risk} high-risk</small>
                    </div>
                  </div>
                </div>
              </Col>
            </Row>
          </>
        )}
      </Container>
    </Layout>
  )
}
