"use client";

import React, { useState } from "react";
import { TrendingUp, Download, Filter, RotateCcw } from "lucide-react";
import { useMetricsData } from "@/app/hooks/dashboard/useMetricsData";
import { useFilters } from "@/app/hooks/dashboard/useFilters";
import { exportData } from "@/app/utils/exportData";

interface AdvancedMetricsDashboardProps {
  autoRefresh?: boolean;
}

export function AdvancedMetricsDashboard({ autoRefresh = true }: AdvancedMetricsDashboardProps) {
  const {
    metrics,
    history,
    isLoading,
    autoRefresh: isAutoRefresh,
    setAutoRefresh,
    refreshInterval,
    setRefreshInterval,
    fetchMetrics,
    getTrend,
    getAverage,
  } = useMetricsData();

  const { filters, updateFilter, resetFilters, getActiveFilterCount } = useFilters();
  const [showFilters, setShowFilters] = useState(false);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  const handleExport = (format: "csv" | "json") => {
    if (!history.length) return;

    const headers = ["timestamp", "slo_compliance_rate", "average_latency_ms", "high_risk_count"];
    const data = history.map((h) => ({
      timestamp: h.timestamp.toISOString(),
      slo_compliance_rate: h.slo_compliance_rate,
      average_latency_ms: h.average_latency_ms,
      high_risk_count: h.high_risk_count,
    }));

    if (format === "csv") {
      exportData.toCSV(data, headers, {
        filename: `metrics-${new Date().toISOString().slice(0, 10)}.csv`,
      });
    } else {
      exportData.toJSON(data, {
        filename: `metrics-${new Date().toISOString().slice(0, 10)}.json`,
      });
    }
  };

  const getTrendColor = (trend: number) => {
    if (trend > 0) return "text-green-600";
    if (trend < 0) return "text-red-600";
    return "text-gray-600";
  };

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Metrics Dashboard</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setAutoRefresh(!isAutoRefresh)}
              className={`px-3 py-2 rounded text-sm font-medium ${
                isAutoRefresh ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
              }`}
            >
              {isAutoRefresh ? "Auto Refresh ON" : "Auto Refresh OFF"}
            </button>
            <button
              onClick={fetchMetrics}
              disabled={isLoading}
              className="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 disabled:bg-gray-300"
            >
              {isLoading ? "Loading..." : "Refresh"}
            </button>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex gap-2 items-center">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm"
          >
            <Filter className="w-4 h-4" />
            Filters ({getActiveFilterCount()})
          </button>

          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded text-sm"
          >
            <option value={10000}>10 seconds</option>
            <option value={30000}>30 seconds</option>
            <option value={60000}>1 minute</option>
            <option value={300000}>5 minutes</option>
          </select>

          <div className="ml-auto flex gap-2">
            <button
              onClick={() => handleExport("csv")}
              className="flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600"
            >
              <Download className="w-4 h-4" />
              CSV
            </button>
            <button
              onClick={() => handleExport("json")}
              className="flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded text-sm hover:bg-green-600"
            >
              <Download className="w-4 h-4" />
              JSON
            </button>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded border border-gray-200 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Risk Level</label>
                <select
                  value={filters.riskLevel || "all"}
                  onChange={(e) => updateFilter("riskLevel", e.target.value)}
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded text-sm"
                >
                  <option value="all">All</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <select
                  value={filters.status || "all"}
                  onChange={(e) => updateFilter("status", e.target.value)}
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded text-sm"
                >
                  <option value="all">All</option>
                  <option value="resolved">Resolved</option>
                  <option value="pending">Pending</option>
                  <option value="escalated">Escalated</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">From Date</label>
                <input
                  type="date"
                  value={dateRange.from}
                  onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">To Date</label>
                <input
                  type="date"
                  value={dateRange.to}
                  onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>

            <button
              onClick={resetFilters}
              className="flex items-center gap-2 px-3 py-2 bg-gray-300 text-gray-800 rounded text-sm hover:bg-gray-400"
            >
              <RotateCcw className="w-4 h-4" />
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* SLO Compliance */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">SLO Compliance</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(metrics.slo_compliance_rate * 100).toFixed(1)}%
                </p>
              </div>
              <TrendingUp className={`w-8 h-8 ${getTrendColor(getTrend("slo_compliance_rate"))}`} />
            </div>
            <p className={`text-xs mt-2 ${getTrendColor(getTrend("slo_compliance_rate"))}`}>
              {getTrend("slo_compliance_rate") > 0 ? "+" : ""}
              {getTrend("slo_compliance_rate").toFixed(1)}% trend
            </p>
          </div>

          {/* Average Latency */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Latency</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.average_latency_ms.toFixed(0)}ms</p>
              </div>
              <TrendingUp className={`w-8 h-8 ${getTrendColor(-getTrend("average_latency_ms"))}`} />
            </div>
            <p className={`text-xs mt-2 ${getTrendColor(-getTrend("average_latency_ms"))}`}>
              {-getTrend("average_latency_ms") > 0 ? "+" : ""}
              {(-getTrend("average_latency_ms")).toFixed(1)}% trend
            </p>
          </div>

          {/* High Risk Count */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Risk</p>
                <p className="text-2xl font-bold text-red-600">{metrics.high_risk_count}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-red-600" />
            </div>
            <p className="text-xs mt-2 text-gray-600">Queries to review</p>
          </div>

          {/* Success Rate */}
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-green-600">{(metrics.success_rate * 100).toFixed(1)}%</p>
              </div>
              <TrendingUp className={`w-8 h-8 ${getTrendColor(getTrend("success_rate"))}`} />
            </div>
            <p className={`text-xs mt-2 ${getTrendColor(getTrend("success_rate"))}`}>
              {getTrend("success_rate") > 0 ? "+" : ""}
              {getTrend("success_rate").toFixed(1)}% trend
            </p>
          </div>
        </div>
      )}

      {/* History Stats */}
      {history.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Time-Based Averages (Last 60 minutes)</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Avg SLO Compliance</p>
              <p className="text-lg font-bold text-gray-900">{(getAverage("slo_compliance_rate") * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Latency</p>
              <p className="text-lg font-bold text-gray-900">{getAverage("average_latency_ms").toFixed(0)}ms</p>
            </div>
            <div>
              <p className="text-gray-600">Avg Success Rate</p>
              <p className="text-lg font-bold text-gray-900">{(getAverage("success_rate") * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-gray-600">Data Points</p>
              <p className="text-lg font-bold text-gray-900">{history.length}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
