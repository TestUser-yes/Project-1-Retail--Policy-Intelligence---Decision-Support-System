"use client";

import React from "react";
import { TrendingUp, AlertCircle, CheckCircle } from "lucide-react";

interface ComplianceMetrics {
  total_queries: number;
  slo_compliance_rate: number;
  escalation_rate: number;
  average_latency_ms: number;
  high_risk_count: number;
  success_rate: number;
}

interface ComplianceDashboardProps {
  metrics: ComplianceMetrics;
}

export function ComplianceDashboard({ metrics }: ComplianceDashboardProps) {
  const isCompliant = metrics.slo_compliance_rate >= 90;
  const latencyOk = metrics.average_latency_ms <= 3000;

  const metricCard = (label: string, value: string | number, unit: string = "", status?: "good" | "warning" | "critical") => {
    const statusClass = {
      good: "text-green-600",
      warning: "text-yellow-600",
      critical: "text-red-600",
    };

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <p className="text-xs text-gray-600 uppercase mb-2">{label}</p>
        <div className="flex items-baseline gap-2">
          <p className={`text-2xl font-bold ${status ? statusClass[status] : "text-gray-900"}`}>{value}</p>
          <p className="text-sm text-gray-600">{unit}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="grid grid-cols-2 gap-4">
        <div className={`rounded-lg p-4 ${isCompliant ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
          <div className="flex items-center gap-3">
            {isCompliant ? (
              <CheckCircle className="w-8 h-8 text-green-600" />
            ) : (
              <AlertCircle className="w-8 h-8 text-red-600" />
            )}
            <div>
              <p className="text-xs text-gray-600 uppercase">SLO Compliance</p>
              <p className={`text-2xl font-bold ${isCompliant ? "text-green-600" : "text-red-600"}`}>
                {metrics.slo_compliance_rate.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className={`rounded-lg p-4 ${latencyOk ? "bg-blue-50 border border-blue-200" : "bg-orange-50 border border-orange-200"}`}>
          <div className="flex items-center gap-3">
            <TrendingUp className={`w-8 h-8 ${latencyOk ? "text-blue-600" : "text-orange-600"}`} />
            <div>
              <p className="text-xs text-gray-600 uppercase">Avg Latency</p>
              <p className={`text-2xl font-bold ${latencyOk ? "text-blue-600" : "text-orange-600"}`}>
                {metrics.average_latency_ms.toFixed(0)}ms
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4">
        {metricCard("Total Queries", metrics.total_queries, "")}
        {metricCard("Success Rate", metrics.success_rate.toFixed(1), "%", "good")}
        {metricCard("High Risk Count", metrics.high_risk_count, "", metrics.high_risk_count > 0 ? "warning" : "good")}
        {metricCard("Escalation Rate", metrics.escalation_rate.toFixed(2), "%")}
      </div>

      {/* Target Achievement */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-4">SLO Targets</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700">Task Success Rate</span>
              <span className="font-semibold">{metrics.success_rate.toFixed(1)}% / 90%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all"
                style={{ width: `${Math.min((metrics.success_rate / 90) * 100, 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700">Latency (P95)</span>
              <span className="font-semibold">{metrics.average_latency_ms.toFixed(0)}ms / 3000ms</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${metrics.average_latency_ms <= 3000 ? "bg-green-500" : "bg-orange-500"}`}
                style={{ width: `${Math.min((metrics.average_latency_ms / 3000) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
