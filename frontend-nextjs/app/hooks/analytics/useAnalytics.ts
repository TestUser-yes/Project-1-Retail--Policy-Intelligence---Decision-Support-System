"use client";

import { useState, useCallback } from "react";

export interface AnalyticsData {
  date: Date;
  total_queries: number;
  success_count: number;
  escalation_count: number;
  avg_latency: number;
  avg_confidence: number;
  high_risk_count: number;
}

export function useAnalytics() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchAnalytics = useCallback(async (days: number = 30) => {
    setIsLoading(true);
    try {
      // TODO: Fetch from API
      setAnalyticsData([]);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getTrends = useCallback(() => {
    if (analyticsData.length < 2) return null;

    const latest = analyticsData[analyticsData.length - 1];
    const previous = analyticsData[analyticsData.length - 2];

    return {
      queries_trend: ((latest.total_queries - previous.total_queries) / previous.total_queries) * 100,
      success_trend: ((latest.success_count - previous.success_count) / previous.success_count) * 100,
      escalation_trend: ((latest.escalation_count - previous.escalation_count) / Math.max(previous.escalation_count, 1)) * 100,
      latency_trend: ((latest.avg_latency - previous.avg_latency) / previous.avg_latency) * 100,
    };
  }, [analyticsData]);

  const getAverages = useCallback(() => {
    if (analyticsData.length === 0) {
      return {
        avg_queries: 0,
        avg_success_rate: 0,
        avg_escalation_rate: 0,
        avg_latency: 0,
        avg_confidence: 0,
      };
    }

    return {
      avg_queries:
        analyticsData.reduce((sum, d) => sum + d.total_queries, 0) / analyticsData.length,
      avg_success_rate:
        (analyticsData.reduce((sum, d) => sum + d.success_count, 0) /
          analyticsData.reduce((sum, d) => sum + d.total_queries, 0)) *
        100,
      avg_escalation_rate:
        (analyticsData.reduce((sum, d) => sum + d.escalation_count, 0) /
          analyticsData.reduce((sum, d) => sum + d.total_queries, 0)) *
        100,
      avg_latency:
        analyticsData.reduce((sum, d) => sum + d.avg_latency, 0) / analyticsData.length,
      avg_confidence:
        analyticsData.reduce((sum, d) => sum + d.avg_confidence, 0) / analyticsData.length,
    };
  }, [analyticsData]);

  return {
    analyticsData,
    isLoading,
    fetchAnalytics,
    getTrends,
    getAverages,
  };
}
