import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Form, Button, Card, Alert } from 'react-bootstrap'
import { useAuth } from '@/context/AuthContext'

export const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login()
      navigate('/')
    } catch (err) {
      setError('Failed to login. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Card className="shadow-lg">
          <Card.Body className="p-5">
            <div className="text-center mb-4">
              <h2 className="mb-2">
                <i className="bi bi-lightning-charge-fill me-2 text-primary"></i>
                Policy AI
              </h2>
              <p className="text-muted">Intelligent Policy Compliance System</p>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <Form onSubmit={handleLogin}>
              <Form.Group className="mb-3">
                <Form.Label>Demo Login</Form.Label>
                <Form.Text className="d-block text-muted mb-3">
                  Click the login button to get started with demo credentials
                </Form.Text>
                <Button
                  variant="primary"
                  type="submit"
                  size="lg"
                  className="w-100"
                  disabled={loading}
                >
                  {loading ? 'Logging in...' : 'Login as Demo User'}
                </Button>
              </Form.Group>
            </Form>

            <hr />

            <div className="alert alert-info small">
              <strong>Demo Credentials:</strong>
              <ul className="mb-0 mt-2">
                <li>User: demo</li>
                <li>Role: user</li>
                <li>Email: demo@retailpolicy.local</li>
              </ul>
            </div>
          </Card.Body>
        </Card>
      </Container>
    </div>
  )
}
