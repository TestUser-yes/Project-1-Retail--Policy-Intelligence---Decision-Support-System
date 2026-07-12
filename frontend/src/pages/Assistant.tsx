import React, { useEffect, useRef, useState } from 'react'
import { Container, Form, Button, Row, Col, Badge } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { ErrorAlert } from '@/components/ErrorAlert'
import { queryApi } from '@/api/query'
import { AskResponse, ConversationMessage } from '@/types'
import { useNotification } from '@/hooks/useNotification'

export const Assistant: React.FC = () => {
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [conversationId] = useState(
    `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  )
  const [currentResponse, setCurrentResponse] = useState<AskResponse | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { notifications, addNotification, removeNotification } = useNotification()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setError('')
    setLoading(true)

    const userMessage: ConversationMessage = {
      role: 'user',
      content: query,
    }

    setMessages((prev) => [...prev, userMessage])
    setQuery('')

    try {
      const response = await queryApi.ask({
        query: userMessage.content,
        conversation_id: conversationId,
      })

      setCurrentResponse(response)

      const assistantMessage: ConversationMessage = {
        role: 'assistant',
        content: response.result.result,
      }

      setMessages((prev) => [...prev, assistantMessage])
      addNotification(
        `Query processed in ${response.latency_seconds.toFixed(2)}s with ${(response.confidence_score * 100).toFixed(0)}% confidence`,
        'success',
        3000
      )
    } catch (err) {
      setError('Failed to process query. Please try again.')
      console.error(err)
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <Container fluid className="h-100">
        <Row className="h-100">
          <Col lg={8} className="d-flex flex-column">
            <h1 className="mb-3">
              <i className="bi bi-chat-dots me-2"></i>
              Policy Assistant
            </h1>

            {error && <ErrorAlert message={error} onClose={() => setError('')} />}

            <div
              className="flex-grow-1 p-3 mb-3"
              style={{
                background: '#f8f9fa',
                borderRadius: '8px',
                overflowY: 'auto',
                border: '1px solid #dee2e6',
              }}
            >
              {messages.length === 0 ? (
                <div className="text-center text-muted py-5">
                  <h6>Start a conversation</h6>
                  <p>Ask me anything about policies, vendors, or compliance</p>
                </div>
              ) : (
                <>
                  {messages.map((msg, i) => (
                    <div
                      key={i}
                      className={`mb-3 d-flex ${msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                    >
                      <div
                        style={{
                          maxWidth: '70%',
                          padding: '12px 16px',
                          borderRadius: '8px',
                          background:
                            msg.role === 'user'
                              ? '#0d6efd'
                              : '#fff',
                          color: msg.role === 'user' ? '#fff' : '#000',
                          border: msg.role === 'assistant' ? '1px solid #dee2e6' : 'none',
                          wordWrap: 'break-word',
                        }}
                      >
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="mb-3">
                      <div
                        style={{
                          padding: '12px 16px',
                          background: '#fff',
                          borderRadius: '8px',
                          border: '1px solid #dee2e6',
                        }}
                      >
                        <div className="spinner-border spinner-border-sm me-2" role="status">
                          <span className="visually-hidden">Loading...</span>
                        </div>
                        Processing...
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-0">
                <div className="input-group">
                  <Form.Control
                    as="textarea"
                    rows={3}
                    placeholder="Ask a question about policies, vendors, or compliance..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={loading}
                    onKeyDown={(e) => {
                      if (e.ctrlKey && e.key === 'Enter') {
                        handleSubmit(e as any)
                      }
                    }}
                  />
                </div>
                <small className="text-muted d-block mt-2">
                  Press Ctrl+Enter or click Send to submit
                </small>
              </Form.Group>
              <Button
                variant="primary"
                type="submit"
                disabled={loading || !query.trim()}
                className="mt-2 w-100"
              >
                {loading ? 'Processing...' : 'Send'}
              </Button>
            </Form>
          </Col>

          <Col lg={4} className="ps-3">
            <div className="card sticky-top" style={{ top: '20px' }}>
              <div className="card-header">
                <h6 className="mb-0">Response Details</h6>
              </div>
              <div className="card-body">
                {currentResponse ? (
                  <>
                    <div className="mb-3">
                      <small className="text-muted">Route</small>
                      <div className="badge bg-info">{currentResponse.route}</div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Confidence</small>
                      <div className="h6 mb-0">
                        {(currentResponse.confidence_score * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Latency</small>
                      <div className="h6 mb-0">{currentResponse.latency_seconds.toFixed(3)}s</div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Cost</small>
                      <div className="h6 mb-0">${currentResponse.cost_usd.toFixed(4)}</div>
                    </div>

                    <div className="mb-3">
                      <small className="text-muted">Risk Level</small>
                      <div>
                        <Badge
                          bg={
                            currentResponse.risk.risk_level === 'high'
                              ? 'danger'
                              : currentResponse.risk.risk_level === 'medium'
                                ? 'warning'
                                : 'success'
                          }
                        >
                          {currentResponse.risk.risk_level}
                        </Badge>
                      </div>
                    </div>

                    {/* SLO Metrics Section */}
                    {currentResponse.slo_metrics && (
                      <>
                        <hr className="my-3" />
                        <small className="text-muted d-block mb-2 fw-bold">SLO Metrics</small>

                        <div className="mb-2">
                          <small className="text-muted">SLO Status</small>
                          <div>
                            <Badge
                              bg={
                                currentResponse.slo_metrics.slo_breached
                                  ? 'danger'
                                  : currentResponse.slo_metrics.slo_status === 'pass'
                                    ? 'success'
                                    : 'warning'
                              }
                            >
                              {currentResponse.slo_metrics.slo_breached ? 'Breached' : 'Healthy'}
                            </Badge>
                          </div>
                        </div>

                        <div className="mb-2">
                          <small className="text-muted">Latency Target</small>
                          <div className="small">
                            {(currentResponse.latency_seconds * 1000).toFixed(0)}ms / {(currentResponse.slo_metrics.target_latency_ms / 1000).toFixed(2)}s
                            <span
                              className={currentResponse.latency_seconds * 1000 <= currentResponse.slo_metrics.target_latency_ms ? 'text-success' : 'text-warning'}
                            >
                              {' '}
                              {currentResponse.latency_seconds * 1000 <= currentResponse.slo_metrics.target_latency_ms ? '✓' : '⚠'}
                            </span>
                          </div>
                        </div>

                        {currentResponse.slo_metrics.enforcement_action && (
                          <div className="mb-2">
                            <small className="text-muted">Enforcement Action</small>
                            <div className="small">
                              <Badge bg="info">{currentResponse.slo_metrics.enforcement_action}</Badge>
                            </div>
                          </div>
                        )}

                        {currentResponse.slo_metrics.enforcement_reason && (
                          <div className="mb-2">
                            <small className="text-muted">Reason</small>
                            <div className="small text-muted">{currentResponse.slo_metrics.enforcement_reason}</div>
                          </div>
                        )}
                      </>
                    )}

                    {currentResponse.sources.length > 0 && (
                      <div>
                        <hr className="my-3" />
                        <small className="text-muted d-block mb-2">Sources</small>
                        <ul className="small mb-0">
                          {currentResponse.sources.slice(0, 3).map((s, i) => (
                            <li key={i}>
                              {s.document} (p.{s.page})
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <p className="text-muted small">Response details will appear here</p>
                )}
              </div>
            </div>
          </Col>
        </Row>
      </Container>

      {notifications.length > 0 && (
        <div
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: 9999,
            maxWidth: '300px',
          }}
        >
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`alert alert-${
                n.type === 'error'
                  ? 'danger'
                  : n.type === 'success'
                    ? 'success'
                    : n.type === 'warning'
                      ? 'warning'
                      : 'info'
              } alert-dismissible mb-2`}
            >
              {n.message}
              <button
                type="button"
                className="btn-close"
                onClick={() => removeNotification(n.id)}
              ></button>
            </div>
          ))}
        </div>
      )}
    </Layout>
  )
}
