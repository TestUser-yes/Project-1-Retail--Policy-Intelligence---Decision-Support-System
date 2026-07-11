"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, Filter } from "lucide-react";

interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  old_value?: string;
  new_value?: string;
  ip_address: string;
  timestamp: string;
}

interface AuditLogViewerProps {
  logs: AuditLog[];
  onFilter?: (filters: Record<string, string>) => void;
}

export function AuditLogViewer({ logs, onFilter }: AuditLogViewerProps) {
  const [expandedLog, setExpandedLog] = useState<string | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [showFilters, setShowFilters] = useState(false);

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilter?.(newFilters);
  };

  const getActionColor = (action: string) => {
    if (action.includes("create") || action.includes("add")) return "bg-green-100 text-green-800";
    if (action.includes("delete") || action.includes("remove")) return "bg-red-100 text-red-800";
    if (action.includes("update") || action.includes("edit")) return "bg-blue-100 text-blue-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Audit Log</h3>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
        >
          <Filter className="w-4 h-4" />
          Filter
        </button>
      </div>

      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Filter by action..."
              onChange={(e) => handleFilterChange("action", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <input
              type="text"
              placeholder="Filter by user..."
              onChange={(e) => handleFilterChange("user_id", e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
        </div>
      )}

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.map((log) => (
          <div
            key={log.id}
            className="border border-gray-200 rounded-lg p-3 cursor-pointer hover:bg-gray-50"
            onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${getActionColor(log.action)}`}>
                  {log.action.toUpperCase()}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-gray-900 text-sm">
                    {log.resource_type}: {log.resource_id}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(log.timestamp).toLocaleString()} • {log.user_id}
                  </p>
                </div>
              </div>
              <div>
                {expandedLog === log.id ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </div>

            {expandedLog === log.id && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                {log.old_value && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700">Previous Value:</p>
                    <p className="text-xs bg-red-50 p-2 rounded font-mono text-gray-900">{log.old_value}</p>
                  </div>
                )}
                {log.new_value && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700">New Value:</p>
                    <p className="text-xs bg-green-50 p-2 rounded font-mono text-gray-900">{log.new_value}</p>
                  </div>
                )}
                <div className="text-xs text-gray-600">
                  <p>IP: {log.ip_address}</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
