import apiClient from './client'
import { AskRequest, AskResponse, ConversationHistory } from '@/types'

export const queryApi = {
  ask: async (request: AskRequest): Promise<AskResponse> => {
    return apiClient.post('/ask', request)
  },

  getConversationHistory: async (conversationId: string): Promise<ConversationHistory> => {
    return apiClient.get(`/conversations/${conversationId}/history`)
  },
}
