import React from 'react'
import { Container } from 'react-bootstrap'
import { Layout } from '@/components/Layout'
import { useAuth } from '@/context/AuthContext'
import { Navigate } from 'react-router-dom'

export const Admin: React.FC = () => {
  const { user } = useAuth()

  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />
  }

  return (
    <Layout>
      <Container fluid>
        <h1 className="mb-4">
          <i className="bi bi-gear me-2"></i>
          Admin Panel
        </h1>

        <div className="card">
          <div className="card-header">
            <h6 className="mb-0">System Configuration</h6>
          </div>
          <div className="card-body">
            <p className="text-muted">Admin features coming soon...</p>

            <div className="row mt-4">
              <div className="col-md-6">
                <h6>User Management</h6>
                <p className="text-muted small">Manage user accounts and permissions</p>
              </div>
              <div className="col-md-6">
                <h6>System Settings</h6>
                <p className="text-muted small">Configure system parameters and thresholds</p>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </Layout>
  )
}
