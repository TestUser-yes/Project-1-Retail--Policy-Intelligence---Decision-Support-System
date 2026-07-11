"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, Clock } from "lucide-react";

interface AgentTrace {
  agent_name: string;
  step_number: number;
  status: "success" | "error" | "pending" | "running";
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  duration_ms: number;
  confidence: number;
  error?: string;
  timestamp: string;
}

interface AgentTraceViewerProps {
  traces: AgentTrace[];
  queryId: string;
}

export function AgentTraceViewer({ traces, queryId }: AgentTraceViewerProps) {
  const [expandedAgent, setExpandedAgent] = useState<number | null>(0);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "running":
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-50 border-green-200";
      case "error":
        return "bg-red-50 border-red-200";
      case "running":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900">Agent Execution Trace</h3>
      <div className="space-y-2">
        {traces.map((trace, idx) => (
          <div
            key={idx}
            className={`border rounded-lg p-3 cursor-pointer transition ${getStatusColor(trace.status)}`}
            onClick={() => setExpandedAgent(expandedAgent === idx ? null : idx)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                {getStatusIcon(trace.status)}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">
                    {trace.step_number}. {trace.agent_name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {trace.duration_ms.toFixed(1)}ms • Confidence: {(trace.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              <div>
                {expandedAgent === idx ? (
                  <ChevronUp className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                )}
              </div>
            </div>

            {expandedAgent === idx && (
              <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                {trace.error && (
                  <div className="bg-red-100 border border-red-300 rounded p-2">
                    <p className="text-sm text-red-800 font-mono">{trace.error}</p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs font-semibold text-gray-700 uppercase">Input</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
                      {JSON.stringify(trace.input_data, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-700 uppercase">Output</p>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
                      {JSON.stringify(trace.output_data, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
