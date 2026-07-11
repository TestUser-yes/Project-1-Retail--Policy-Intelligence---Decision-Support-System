"use client";

import React, { useState, useEffect } from "react";
import { AgentStatusBoard } from "@/app/components/AgentStatusBoard";
import { ComplianceDashboard } from "@/app/components/ComplianceDashboard";
import { EscalationPanel } from "@/app/components/EscalationPanel";
import { RefreshCw } from "lucide-react";

export default function AdminPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [metrics, setMetrics] = useState(null);
  const [escalations, setEscalations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
    const interval = setInterval(fetchAdminData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAdminData = async () => {
    try {
      const [agentsRes, metricsRes, escalationsRes] = await Promise.all([
        fetch("/api/agents/status"),
        fetch("/api/audit/compliance-status"),
        fetch("/api/escalation/pending"),
      ]);

      if (agentsRes.ok) {
        const data = await agentsRes.json();
        setAgents(Object.entries(data.agents || {}).map(([name, info]: any) => ({
          name,
          ...info,
        })));
      }

      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }

      if (escalationsRes.ok) {
        const data = await escalationsRes.json();
        setEscalations(data.escalations || []);
      }
    } catch (error) {
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-2">System monitoring and escalation management</p>
          </div>
          <button
            onClick={fetchAdminData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Compliance Dashboard */}
          <div className="lg:col-span-2">
            {metrics ? (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <ComplianceDashboard metrics={metrics} />
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-6 text-center text-gray-600">
                Loading metrics...
              </div>
            )}
          </div>

          {/* Right Column - Agent Status */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            {agents.length > 0 ? (
              <AgentStatusBoard agents={agents} />
            ) : (
              <div className="text-center text-gray-600">Loading agents...</div>
            )}
          </div>
        </div>

        {/* Escalation Panel */}
        <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
          <EscalationPanel escalations={escalations} />
        </div>
      </div>
    </div>
  );
}
