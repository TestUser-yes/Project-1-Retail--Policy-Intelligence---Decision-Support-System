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

// Dashboard types
export interface DashboardData {
  total_queries: number
  total_documents: number
  total_vendors: number
  average_confidence: number
  total_cost_usd: number
  slo_violations: number
  active_conversations: number
  system_health: 'healthy' | 'degraded' | 'unhealthy'
  recent_queries: Array<{
    query: string
    confidence: number
    cost_usd: number
    timestamp: string
  }>
  documents_stats: {
    total: number
    processed: number
    indexed: number
  }
  vendors_stats: {
    total: number
    active: number
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
  size: number
  chunks: number
  message: string
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

// Observability types
export interface ObservabilityData {
  langfuse_status: string
  langfuse_token_usage: {
    input_tokens: number
    output_tokens: number
    total_tokens: number
  }
  demo_agents: string[]
  system_info: {
    uptime_seconds: number
    active_connections: number
    database_queries: number
  }
}
