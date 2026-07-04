"use client";

import { useState, useCallback, useEffect } from "react";

export interface MetricsData {
  timestamp: Date;
  slo_compliance_rate: number;
  average_latency_ms: number;
  high_risk_count: number;
  escalation_rate: number;
  success_rate: number;
  total_queries: number;
}

export function useMetricsData() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [history, setHistory] = useState<MetricsData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  // Fetch current metrics
  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/audit/compliance-status");
      if (response.ok) {
        const data = await response.json();
        const metricsData: MetricsData = {
          ...data,
          timestamp: new Date(),
        };
        setMetrics(metricsData);
        setHistory((prev) => [...prev.slice(-99), metricsData]); // Keep last 100 data points
      }
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-refresh setup
  useEffect(() => {
    fetchMetrics(); // Fetch immediately

    if (!autoRefresh) return;

    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchMetrics]);

  // Get metrics trend
  const getTrend = useCallback((metric: keyof Omit<MetricsData, "timestamp">) => {
    if (history.length < 2) return 0;

    const recent = history[history.length - 1][metric];
    const previous = history[history.length - 2][metric];
    return ((recent - previous) / previous) * 100;
  }, [history]);

  // Get average over time range
  const getAverage = useCallback((metric: keyof Omit<MetricsData, "timestamp">, minutes: number = 60) => {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    const filtered = history.filter((h) => h.timestamp >= cutoff);

    if (filtered.length === 0) return 0;

    return filtered.reduce((sum, h) => sum + h[metric], 0) / filtered.length;
  }, [history]);

  return {
    metrics,
    history,
    isLoading,
    autoRefresh,
    setAutoRefresh,
    refreshInterval,
    setRefreshInterval,
    fetchMetrics,
    getTrend,
    getAverage,
  };
}
