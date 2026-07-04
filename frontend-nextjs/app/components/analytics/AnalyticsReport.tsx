"use client";

import React, { useEffect } from "react";
import { TrendingUp, TrendingDown, BarChart3 } from "lucide-react";
import { useAnalytics } from "@/app/hooks/analytics/useAnalytics";

interface AnalyticsReportProps {
  days?: number;
}

export function AnalyticsReport({ days = 30 }: AnalyticsReportProps) {
  const { analyticsData, isLoading, fetchAnalytics, getTrends, getAverages } = useAnalytics();

  useEffect(() => {
    fetchAnalytics(days);
  }, [days, fetchAnalytics]);

  const trends = getTrends();
  const averages = getAverages();

  const TrendIndicator = ({ value, unit = "%" }: { value: number; unit?: string }) => {
    const isPositive = value > 0;
    return (
      <div className={`flex items-center gap-1 text-xs font-semibold ${isPositive ? "text-green-600" : "text-red-600"}`}>
        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        {Math.abs(value).toFixed(1)}{unit}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Analytics Report
        </h2>
        <select
          defaultValue={days}
          onChange={(e) => fetchAnalytics(parseInt(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-gray-600">Loading analytics...</div>
      ) : analyticsData.length === 0 ? (
        <div className="text-center py-8 text-gray-600">No analytics data available</div>
      ) : (
        <>
          {/* Trends */}
          {trends && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 mb-2">Queries Trend</p>
                <TrendIndicator value={trends.queries_trend} />
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 mb-2">Success Trend</p>
                <TrendIndicator value={trends.success_trend} />
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 mb-2">Escalation Trend</p>
                <TrendIndicator value={trends.escalation_trend} unit=" escalations" />
              </div>
              <div className="bg-white rounded-lg shadow p-4">
                <p className="text-sm text-gray-600 mb-2">Latency Trend</p>
                <TrendIndicator value={-trends.latency_trend} />
              </div>
            </div>
          )}

          {/* Averages */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Average Metrics</h3>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <p className="text-xs text-gray-600 uppercase">Avg Queries/Day</p>
                <p className="text-2xl font-bold text-gray-900">{averages.avg_queries.toFixed(0)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 uppercase">Success Rate</p>
                <p className="text-2xl font-bold text-green-600">{averages.avg_success_rate.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 uppercase">Escalation Rate</p>
                <p className="text-2xl font-bold text-orange-600">{averages.avg_escalation_rate.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 uppercase">Avg Latency</p>
                <p className="text-2xl font-bold text-blue-600">{averages.avg_latency.toFixed(0)}ms</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 uppercase">Avg Confidence</p>
                <p className="text-2xl font-bold text-purple-600">{(averages.avg_confidence * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>

          {/* Timeline Data */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Date</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Queries</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Success</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Escalations</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Latency</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsData.slice(-10).reverse().map((data, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {data.date.toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{data.total_queries}</td>
                      <td className="px-4 py-3 text-sm text-green-600">{data.success_count}</td>
                      <td className="px-4 py-3 text-sm text-orange-600">{data.escalation_count}</td>
                      <td className="px-4 py-3 text-sm text-blue-600">{data.avg_latency.toFixed(0)}ms</td>
                      <td className="px-4 py-3 text-sm text-purple-600">
                        {(data.avg_confidence * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
