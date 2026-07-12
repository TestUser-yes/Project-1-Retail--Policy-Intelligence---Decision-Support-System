import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Container, Navbar, Nav, Button } from 'react-bootstrap'

interface LayoutProps {
  children: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="app-container">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="p-3">
          <h5 className="text-white mb-4">
            <i className="bi bi-lightning-charge-fill me-2"></i>
            Policy AI
          </h5>
          <Nav className="flex-column">
            <Nav.Link href="/" className="text-white py-2 rounded mb-2">
              <i className="bi bi-house me-2"></i>Dashboard
            </Nav.Link>
            <Nav.Link href="/assistant" className="text-white py-2 rounded mb-2">
              <i className="bi bi-chat-dots me-2"></i>Assistant
            </Nav.Link>
            <Nav.Link href="/documents" className="text-white py-2 rounded mb-2">
              <i className="bi bi-file-earmark me-2"></i>Documents
            </Nav.Link>
            {user?.role === 'admin' && (
              <>
                <hr className="bg-light" />
                <Nav.Link href="/admin" className="text-white py-2 rounded mb-2">
                  <i className="bi bi-gear me-2"></i>Admin
                </Nav.Link>
              </>
            )}
            <hr className="bg-light" />
            <Nav.Link
              href="#"
              className="text-white py-2 rounded"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <i className="bi bi-chevron-left me-2"></i>
              {sidebarOpen ? 'Hide' : 'Show'}
            </Nav.Link>
          </Nav>
        </div>
      </aside>

      <div className="main-content">
        <Navbar className="navbar-custom">
          <Container fluid>
            <Navbar.Text className="me-auto">
              <i className="bi bi-info-circle me-2"></i>
              {user?.username && `Welcome User, ${user.username}`}
            </Navbar.Text>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </Container>
        </Navbar>

        <div className="content">
          {children}
        </div>
      </div>
    </div>
  )
}
