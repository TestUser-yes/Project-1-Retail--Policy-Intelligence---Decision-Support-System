import apiClient from './client'
import { DocumentList, IngestionResponse, Document } from '@/types'

export const documentApi = {
  upload: async (file: File): Promise<IngestionResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.postFormData('/api/ingestion/ingest', formData)
  },

  list: async (): Promise<Document[]> => {
    const response = await apiClient.get<DocumentList>('/api/ingestion/retrieve')
    return response.documents
  },

  delete: async (filename: string): Promise<{ success: boolean }> => {
    return apiClient.delete(`/api/ingestion/delete/${filename}`)
  },
}
