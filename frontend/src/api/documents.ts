import apiClient from './client'
import { IngestionResponse } from '@/types'

export interface RetrieveChunksRequest {
  query: string
  k?: number
}

export interface ChunkData {
  content: string
  metadata: {
    id: number
    document_name: string
    page_number: number
    section: string
    chunk_number: number
  }
}

export interface RetrieveChunksResponse {
  query: string
  chunks: ChunkData[]
  count: number
  timestamp: string
  retrieval_method: string
  retrieval_agents: string[]
  retrieval_pipeline: Record<string, unknown>
}

export const documentApi = {
  /**
   * Upload and index a PDF document
   * Returns ingestion response with document metadata
   */
  upload: async (file: File): Promise<IngestionResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.postFormData('/api/ingestion/ingest', formData)
  },

  /**
   * Retrieve policy chunks using vector similarity search
   * This is the Phase 2 RAG retrieval endpoint
   */
  retrieveChunks: async (request: RetrieveChunksRequest): Promise<RetrieveChunksResponse> => {
    return apiClient.post('/api/ingestion/retrieve', request)
  },
}
