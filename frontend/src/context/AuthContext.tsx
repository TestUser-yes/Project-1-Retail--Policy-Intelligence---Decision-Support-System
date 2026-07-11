import React, { createContext, useContext, useEffect, useState } from 'react'
import { User } from '@/types'
import { authApi } from '@/api/auth'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(authApi.getCurrentUser())
  const [isAuthenticated, setIsAuthenticated] = useState(!!user)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const status = await authApi.getStatus()
      if (status.authenticated && status.user_id) {
        const currentUser: User = {
          user_id: status.user_id,
          username: status.username || '',
          email: status.email || '',
          role: (status.role as User['role']) || 'user',
        }
        setUser(currentUser)
        setIsAuthenticated(true)
        authApi.setCurrentUser(currentUser)
      } else {
        setUser(null)
        setIsAuthenticated(false)
        authApi.clearCurrentUser()
      }
    } catch {
      setUser(null)
      setIsAuthenticated(false)
      authApi.clearCurrentUser()
    } finally {
      setIsLoading(false)
    }
  }

  const login = async () => {
    try {
      await authApi.getToken()
      await checkAuth()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setUser(null)
      setIsAuthenticated(false)
      authApi.clearCurrentUser()
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
