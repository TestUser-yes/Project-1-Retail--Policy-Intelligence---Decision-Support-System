import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Allow credentials (cookies) to be sent with requests
  withCredentials: true,
});

// Token refresh state
let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

// Initialize tokens on app load - now stored in secure httpOnly cookies
async function initializeTokens(): Promise<void> {
  try {
    const response = await axios.post(
      `${API_URL}/token`,
      {},
      { withCredentials: true }
    );
    // Tokens are now set as secure httpOnly cookies by the backend
    // Response contains token info for client-side tracking
  } catch (error) {
    throw new Error('Authentication failed');
  }
}

async function refreshAccessToken(): Promise<boolean> {
  // Prevent multiple simultaneous refresh requests
  if (isRefreshing && refreshPromise) {
    await refreshPromise;
    return true;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      // Backend reads refresh_token from secure cookie and returns new access_token in cookie
      await axios.post(
        `${API_URL}/token/refresh`,
        {},
        { withCredentials: true }
      );
      return '';
    } catch (error) {
      throw new Error('Token refresh failed');
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  try {
    await refreshPromise;
    return true;
  } catch {
    return false;
  }
}

// Response interceptor - handle 401 errors and refresh tokens
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and haven't retried yet, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          // Retry the original request with refreshed token
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Redirect to login or show auth error
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

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

export interface AgentExecution {
  agent_name: string;
  status: string;
  latency_ms: number;
  confidence: number;
  data_source: string;
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
  // Agent execution details
  agents_used?: string[];
  agent_details?: AgentExecution[];
  retrieval_method?: string;
  retrieval_agents?: string[];
  retrieval_pipeline?: Record<string, any>;
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
