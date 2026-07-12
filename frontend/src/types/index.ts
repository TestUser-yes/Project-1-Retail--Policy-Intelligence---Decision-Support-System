// Auth types
export interface User {
  user_id: string
  username: string
  email: string
  role: 'user' | 'compliance_officer' | 'admin'
}

export interface AuthResponse {
  authenticated: boolean
  user_id?: string
  username?: string
  email?: string
  role?: string
  message: string
}

export interface TokenResponse {
  token_type: string
  expires_in: number
  message: string
}

// Query types
export interface AskRequest {
  query: string
  conversation_id?: string
}

export interface IntentModel {
  intent: string
  reason: string
}

export interface ResultModel {
  result: string
}

export interface RiskModel {
  risk_level: 'low' | 'medium' | 'high'
  reason: string
}

export interface SLOMetricsModel {
  latency_ms: number
  target_latency_ms: number
  slo_status: 'pass' | 'fail'
  slo_breached: boolean
  enforcement_action: string
  enforcement_reason: string
}

export interface AgentExecutionModel {
  agent_name: string
  status: string
  latency_ms: number
  confidence: number
  data_source: string
}

export interface RetrievalPipeline {
  semantic_search: { status: string; results: number }
  keyword_search: { status: string; results: number }
  ranking: { status: string; top_k: number }
}

export interface AskResponse {
  query: string
  conversation_id: string
  intent: IntentModel
  route: string
  result: ResultModel
  risk: RiskModel
  escalate: boolean
  escalation_reason: string
  latency_seconds: number
  cost_usd: number
  budget_remaining_usd: number
  budget_percent_used: number
  slo_metrics: SLOMetricsModel
  validation_passed: boolean
  confidence_score: number
  sources: Array<{ document: string; page: number; section: string }>
  sql_validation: string
  recommendation: string
  agents_used: string[]
  agent_details: AgentExecutionModel[]
  retrieval_method: string
  retrieval_agents: string[]
  retrieval_pipeline: RetrievalPipeline
}

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ConversationHistory {
  conversation_id: string
  messages: ConversationMessage[]
}

// Dashboard types - matches backend response schema
export interface DashboardData {
  totalQueries: number
  avgLatency: number
  escalationRate: number
  budgetUsed: number
  budgetUsdLimit: number
  budgetUsdUsed: number
  budgetRemaining: number
  activeUsers: number
  successRate: number
  queryByRoute: {
    rag: number
    sql: number
    hybrid: number
  }
  queryByRisk: {
    low: number
    medium: number
    high: number
  }
  topPolicies: Array<{ name: string; count: number }>
  topIntents: Array<{ name: string; count: number }>
  recentQueries: Array<{
    id: string
    query: string
    route: string
    risk: string
    cost: number
    latency: number
    timestamp: string
  }>
  hourlyTrends: Array<{
    time: string
    queries: number
    latency: number
  }>
  vendorStats: {
    total: number
    high_risk: number
  }
  sloMetrics: {
    success_rate: number
    avg_latency_ms: number
    target_latency_ms: number
    escalation_count: number
  }
}

// Document types
export interface Document {
  filename: string
  size: number
  chunks: number
  indexed_at: string
}

export interface IngestionResponse {
  filename: string
  document_name: string
  chunks_created: number
  total_pages: number
  status: string
  timestamp: string
}

export interface DocumentList {
  documents: Document[]
}

// Error types
export interface ApiError {
  detail?: string
  message?: string
  status?: number
}

// Observability types - matches backend response schema
export interface ObservabilityData {
  timestamp: string
  summary: {
    total_queries: number
    queries_24h: number
    avg_confidence: number
    escalation_rate: number
    slo_compliance_rate: number
  }
  risk_distribution: {
    high: number
    medium: number
    low: number
  }
  route_distribution: {
    rag: number
    sql: number
    hybrid: number
  }
  slo_metrics: {
    success_rate: number
    avg_latency_ms: number
    target_latency_ms: number
    slo_status: 'pass' | 'fail'
  }
  hourly_trends: Array<{
    time: string
    queries: number
    slo_target_ms: number
    avg_latency_ms: number
  }>
  recent_queries: Array<{
    id: string
    query: string
    route: string
    risk: string
    latency_ms: number
    timestamp: string
  }>
  langfuse_traces: any[]
  multi_agent_summary: {
    rag_agent_calls: number
    sql_agent_calls: number
    hybrid_agent_calls: number
    total_agent_calls: number
    agent_routing_efficiency: {
      single_agent_percentage: number
      hybrid_percentage: number
    }
  }
}
