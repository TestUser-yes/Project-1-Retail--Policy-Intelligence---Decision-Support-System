import apiClient from './client'
import { AuthResponse, TokenResponse, User } from '@/types'

export const authApi = {
  getToken: async (): Promise<TokenResponse> => {
    return apiClient.post('/token')
  },

  getStatus: async (): Promise<AuthResponse> => {
    return apiClient.get('/auth/status')
  },

  refreshToken: async (): Promise<TokenResponse> => {
    return apiClient.post('/token/refresh')
  },

  logout: async (): Promise<{ success: boolean; message: string }> => {
    return apiClient.post('/logout')
  },

  getCurrentUser: (): User | null => {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  setCurrentUser: (user: User) => {
    localStorage.setItem('user', JSON.stringify(user))
  },

  clearCurrentUser: () => {
    localStorage.removeItem('user')
  },
}
