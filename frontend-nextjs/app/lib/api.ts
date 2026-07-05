import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Initialize token on app load
let tokenPromise: Promise<string> | null = null;

async function ensureToken(): Promise<string> {
  const cached = localStorage.getItem('access_token');
  if (cached) return cached;

  if (!tokenPromise) {
    tokenPromise = (async () => {
      try {
        const response = await axios.get(`${API_URL}/token`);
        const token = response.data.access_token;
        localStorage.setItem('access_token', token);
        return token;
      } catch (error) {
        console.error('Failed to fetch token:', error);
        throw new Error('Authentication failed');
      }
    })();
  }

  return tokenPromise;
}

apiClient.interceptors.request.use(async (config) => {
  try {
    const token = await ensureToken();
    config.headers.Authorization = `Bearer ${token}`;
  } catch (error) {
    console.error('Token error:', error);
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
  // Phase 7 fields
  confidence_score?: number;
  sources?: Array<string | { source?: string; policy?: string; section?: string; page?: number }>;
  sql_validation?: string | { query: string; status: string; result: any };
  recommendation?: string;
}

export interface DashboardData {
  totalQueries: number;
  avgLatency: number;
  escalationRate: number;
  budgetUsed: number;
  budgetUsdLimit: number;
  budgetUsdUsed: number;
  budgetRemaining: number;
  activeUsers: number;
  successRate: number;
  queryByRoute: { rag: number; sql: number; hybrid: number };
  queryByRisk: { low: number; medium: number; high: number };
  topPolicies: Array<{ name: string; count: number }>;
  topIntents: Array<{ name: string; count: number }>;
  recentQueries: any[];
  hourlyTrends: Array<{ time: string; queries: number; latency: number }>;
  vendorStats: { total: number; high_risk: number };
  sloMetrics: {
    success_rate: number;
    avg_latency_ms: number;
    target_latency_ms: number;
    escalation_count: number;
  };
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

  async getDashboard(): Promise<DashboardData> {
    const response = await apiClient.get('/api/dashboard');
    return response.data;
  },
};

export default apiClient;
