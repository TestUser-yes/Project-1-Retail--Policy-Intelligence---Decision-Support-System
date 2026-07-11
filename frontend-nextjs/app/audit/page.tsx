"use client";

import React, { useState, useEffect } from "react";
import { AuditLogViewer } from "@/app/components/AuditLogViewer";
import { Filter, Download } from "lucide-react";

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await fetch("/api/audit/logs?limit=100");
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      }
    } catch (error) {
    } finally {
      setIsLoading(false);
    }
  };

  const exportLogs = () => {
    const csv = [
      ["ID", "User ID", "Action", "Resource Type", "Resource ID", "Timestamp"],
      ...logs.map((log: any) => [
        log.id,
        log.user_id,
        log.action,
        log.resource_type,
        log.resource_id,
        log.timestamp,
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
            <p className="text-gray-600 mt-2">Complete system audit trail for compliance</p>
          </div>
          <button
            onClick={exportLogs}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-gray-400" />
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              placeholder="From date"
            />
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
              placeholder="To date"
            />
            <button
              onClick={fetchLogs}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
            >
              Filter
            </button>
          </div>
        </div>

        {/* Logs Table */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          {isLoading ? (
            <div className="text-center text-gray-600">Loading logs...</div>
          ) : (
            <AuditLogViewer logs={logs} />
          )}
        </div>
      </div>
    </div>
  );
}
