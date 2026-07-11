import axios, { AxiosInstance, AxiosError } from 'axios'
import { ApiError } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          try {
            await this.refreshToken()
            return this.client.request(error.config!)
          } catch {
            this.logout()
            return Promise.reject(error)
          }
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string) {
    try {
      const response = await this.client.get<T>(url)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async post<T>(url: string, data?: unknown) {
    try {
      const response = await this.client.post<T>(url, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async put<T>(url: string, data?: unknown) {
    try {
      const response = await this.client.put<T>(url, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async delete<T>(url: string) {
    try {
      const response = await this.client.delete<T>(url)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async postFormData<T>(url: string, formData: FormData) {
    try {
      const response = await this.client.post<T>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  private handleError(error: unknown): ApiError {
    if (axios.isAxiosError(error)) {
      return {
        status: error.response?.status,
        message: error.response?.data?.detail || error.message,
      }
    }
    return { message: 'An unexpected error occurred' }
  }

  private async refreshToken() {
    return this.client.post('/token/refresh')
  }

  private logout() {
    localStorage.removeItem('user')
    sessionStorage.clear()
    window.location.href = '/login'
  }

  getClient() {
    return this.client
  }
}

export default new ApiClient()
