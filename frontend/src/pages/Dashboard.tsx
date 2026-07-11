import React, { useEffect, useState } from 'react'
import { Container, Row, Col, Table } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { KPICard } from '@/components/KPICard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorAlert } from '@/components/ErrorAlert'
import { dashboardApi } from '@/api/dashboard'
import { DashboardData } from '@/types'

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
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

    fetchData()
    const interval = setInterval(fetchData, 30000)
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
                  value={data.total_queries}
                  icon="bi-chat-dots"
                  variant="primary"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Documents Indexed"
                  value={data.total_documents}
                  icon="bi-file-earmark"
                  variant="success"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Avg. Confidence"
                  value={`${(data.average_confidence * 100).toFixed(1)}%`}
                  icon="bi-percent"
                  variant="info"
                />
              </Col>
              <Col lg={3} md={6} className="mb-3">
                <KPICard
                  title="Total Cost"
                  value={`$${data.total_cost_usd.toFixed(2)}`}
                  icon="bi-currency-dollar"
                  variant="warning"
                />
              </Col>
            </Row>

            <Row className="mb-4">
              <Col lg={8}>
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0">Recent Queries</h6>
                  </div>
                  <div className="card-body">
                    {data.recent_queries.length > 0 ? (
                      <Table striped hover size="sm">
                        <thead>
                          <tr>
                            <th>Query</th>
                            <th>Confidence</th>
                            <th>Cost</th>
                            <th>Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.recent_queries.map((q, i) => (
                            <tr key={i}>
                              <td className="text-truncate">{q.query}</td>
                              <td>
                                <span className="badge bg-info">
                                  {(q.confidence * 100).toFixed(0)}%
                                </span>
                              </td>
                              <td>${q.cost_usd.toFixed(4)}</td>
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
                    <h6 className="mb-0">System Status</h6>
                  </div>
                  <div className="card-body">
                    <div className="mb-3">
                      <small className="text-muted">System Health</small>
                      <div className="d-flex align-items-center">
                        <span
                          className={`badge bg-${
                            data.system_health === 'healthy' ? 'success' : 'warning'
                          } me-2`}
                        >
                          {data.system_health}
                        </span>
                      </div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Active Conversations</small>
                      <div className="h5 mb-0">{data.active_conversations}</div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Documents</small>
                      <div className="progress" style={{ height: '20px' }}>
                        <div
                          className="progress-bar"
                          style={{
                            width: `${(data.documents_stats.processed / data.documents_stats.total) * 100}%`,
                          }}
                        >
                          {data.documents_stats.indexed}/{data.documents_stats.total}
                        </div>
                      </div>
                    </div>

                    <div>
                      <small className="text-muted">Vendors</small>
                      <div className="h5 mb-0">{data.vendors_stats.active}</div>
                      <small className="text-muted">out of {data.vendors_stats.total}</small>
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
