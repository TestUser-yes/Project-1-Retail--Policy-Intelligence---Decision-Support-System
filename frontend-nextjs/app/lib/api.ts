import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface SLOMetrics {
  latency_ms: number;
  target_latency_ms: number;
  slo_status: 'pass' | 'warning' | 'fail';
}

export interface RiskModel {
  risk_level: string;
  reason: string;
}

export interface IntentModel {
  intent: string;
  reason: string;
}

export interface ResultModel {
  result: string;
}

export interface AskResponse {
  query: string;
  conversation_id: string;
  intent: IntentModel;
  route: string;
  result: ResultModel;
  risk: RiskModel;
  escalate: boolean;
  escalation_reason: string;
  latency_seconds: number;
  cost_usd: number;
  budget_remaining_usd: number;
  budget_percent_used: number;
  slo_metrics: SLOMetrics;
  validation_passed: boolean;
}

export const api = {
  async getToken() {
    const response = await apiClient.get('/token');
    return response.data;
  },

  async getHealth() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  async ask(query: string, conversationId?: string): Promise<AskResponse> {
    const response = await apiClient.post('/ask', {
      query,
      conversation_id: conversationId || undefined,
    });
    return response.data;
  },

  async getConversationHistory(conversationId: string) {
    const response = await apiClient.get(
      `/conversations/${conversationId}/history`
    );
    return response.data;
  },
};

export default apiClient;
