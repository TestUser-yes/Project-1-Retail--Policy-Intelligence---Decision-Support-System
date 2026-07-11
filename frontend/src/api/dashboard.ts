import apiClient from './client'
import { DashboardData, ObservabilityData } from '@/types'

export const dashboardApi = {
  getDashboard: async (): Promise<DashboardData> => {
    return apiClient.get('/api/dashboard')
  },

  getObservability: async (): Promise<ObservabilityData> => {
    return apiClient.get('/api/observability')
  },

  getHealth: async (): Promise<{ status: string }> => {
    return apiClient.get('/health')
  },
}
