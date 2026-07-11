"use client";

import React, { useState } from "react";
import { AlertTriangle, CheckCircle, Clock, X } from "lucide-react";

interface Escalation {
  escalation_id: string;
  query_id: string;
  reason: string;
  priority: "low" | "medium" | "high" | "critical";
  status: "pending_review" | "in_progress" | "resolved";
  created_at: string;
  assigned_to?: string;
}

interface EscalationPanelProps {
  escalations: Escalation[];
  onResolve?: (escalationId: string, resolution: string) => void;
  onAssign?: (escalationId: string, userId: string) => void;
}

export function EscalationPanel({ escalations, onResolve, onAssign }: EscalationPanelProps) {
  const [selectedEscalation, setSelectedEscalation] = useState<string | null>(null);
  const [resolution, setResolution] = useState("");

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-300";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-blue-100 text-blue-800 border-blue-300";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "resolved":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "in_progress":
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
    }
  };

  const pendingCount = escalations.filter((e) => e.status === "pending_review").length;
  const resolvedCount = escalations.filter((e) => e.status === "resolved").length;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-xs text-gray-600 uppercase">Pending</p>
          <p className="text-2xl font-bold text-red-600">{pendingCount}</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-xs text-gray-600 uppercase">In Progress</p>
          <p className="text-2xl font-bold text-blue-600">
            {escalations.filter((e) => e.status === "in_progress").length}
          </p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-xs text-gray-600 uppercase">Resolved</p>
          <p className="text-2xl font-bold text-green-600">{resolvedCount}</p>
        </div>
      </div>

      <div className="space-y-2">
        {escalations.map((escalation) => (
          <div
            key={escalation.escalation_id}
            className={`border rounded-lg p-3 cursor-pointer transition ${
              selectedEscalation === escalation.escalation_id ? "bg-blue-50 border-blue-300" : "hover:bg-gray-50"
            }`}
            onClick={() => setSelectedEscalation(escalation.escalation_id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                {getStatusIcon(escalation.status)}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold border ${getPriorityColor(escalation.priority)}`}>
                      {escalation.priority.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">{escalation.status.replace("_", " ")}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mt-1">{escalation.reason}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Query: {escalation.query_id.slice(0, 8)}... • {new Date(escalation.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {selectedEscalation === escalation.escalation_id && escalation.status === "pending_review" && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-2">Resolution</label>
                  <textarea
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value)}
                    placeholder="Enter resolution notes..."
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    rows={3}
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      onResolve?.(escalation.escalation_id, resolution);
                      setResolution("");
                    }}
                    className="flex-1 px-3 py-2 bg-green-500 text-white rounded text-sm font-medium hover:bg-green-600"
                  >
                    Resolve
                  </button>
                  <button
                    onClick={() => setSelectedEscalation(null)}
                    className="px-3 py-2 bg-gray-200 text-gray-900 rounded text-sm font-medium hover:bg-gray-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
