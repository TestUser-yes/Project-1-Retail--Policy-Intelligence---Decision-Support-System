// Chart data generators and utilities

export interface ChartDataPoint {
  name: string;
  value: number;
  percentage?: number;
}

export interface TimeSeriesData {
  time: string;
  value: number;
  target?: number;
}

export const generatePieChartData = (categories: Record<string, number>) => {
  const total = Object.values(categories).reduce((a, b) => a + b, 0);
  return Object.entries(categories).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    percentage: total > 0 ? (value / total) * 100 : 0,
  }));
};

export const generateLineChartData = (
  labels: string[],
  values: number[],
  targets?: number[]
): TimeSeriesData[] => {
  return labels.map((label, idx) => ({
    time: label,
    value: values[idx] || 0,
    target: targets ? targets[idx] : undefined,
  }));
};

export const generateBarChartData = (items: Record<string, number>) => {
  return Object.entries(items).map(([name, value]) => ({
    name,
    value,
  }));
};

export const COLORS = {
  primary: '#1e3a8a',
  secondary: '#475569',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
  slate: '#e2e8f0',
  gray: '#9ca3af',
};

export const CHART_COLORS = [
  COLORS.primary,
  COLORS.success,
  COLORS.warning,
  COLORS.danger,
  COLORS.info,
  '#8b5cf6',
  '#06b6d4',
  '#ec4899',
];

// Mock data - used only when backend data is unavailable
// These should be fetched from the backend API in production
// According to capstone requirements (capstone_retail_policy_intelligence_dataset.md)

export const mockDashboardMetrics = {
  systemOverview: {
    // From SLO targets in README.md: 90% Task Success Rate
    activeUsers: 0, // Should be fetched from backend
    totalQueries: 0, // Should be fetched from backend
    successRate: 90.0, // SLO target from capstone
    systemHealth: 'healthy' as const,
  },
  realtimeMetrics: {
    queriesLast24h: 0, // Should be fetched from backend
    avgResponseTime: 2.0, // 2 seconds from capstone SLO targets
    escalationRate: 0, // Should be calculated from backend data
    budgetUsed: 0, // Should be tracked from backend
  },
  // Query distribution based on capstone golden queries (50 queries):
  // - Policy Interpretation (RAG): 15
  // - Structured Lookup (SQL): 10
  // - Hybrid Reasoning: 10
  // - High-Risk Regulatory: 10
  // - Escalation Scenarios: 5
  queryDistribution: {
    policy: 0, // Real data from backend
    vendor: 0, // Real data from backend
    hybrid: 0, // Real data from backend
  },
  // Risk distribution - real data should come from database
  riskDistribution: {
    low: 0,
    medium: 0,
    high: 0,
  },
  // Route distribution - from intelligent routing in README.md
  routeDistribution: {
    rag: 0, // Policy explanation, clause interpretation
    sql: 0, // Compliance records, approval status
    hybrid: 0, // Interpretation + structured validation
  },
  // Top policies - from capstone dataset (policy documents)
  topPolicies: [
    { name: 'Retail Data Protection & Customer Privacy Policy', queries: 0 },
    { name: 'Data Retention & Archival Policy', queries: 0 },
    { name: 'Supplier & Vendor Compliance Policy', queries: 0 },
    { name: 'Anti-Bribery & Ethical Conduct Policy', queries: 0 },
    { name: 'Information Security & Access Control Policy', queries: 0 },
  ],
  // Escalations - high-risk scenarios from capstone
  recentEscalations: [
    // These should be fetched from real escalation data
    // Escalation triggers from capstone:
    // - Cross-border data transfer with restricted jurisdictions
    // - Deletion request for records under legal hold
    // - Approval override for Critical-risk vendor
    // - Hospitality/gift approval with overseas suppliers
    // - Overdue audit findings
    // - Conflicting policies
    // - Vendor onboarding with unresolved findings
    // - Closed issues without resolution evidence
  ],
};
