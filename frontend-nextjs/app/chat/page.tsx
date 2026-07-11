"use client";

import React, { useState } from "react";
import { ChatWindow } from "@/app/components/ChatWindow";
import { AgentTraceViewer } from "@/app/components/agent-trace/AgentTraceViewer";
import { Loader } from "lucide-react";

interface QueryResponse {
  id: string;
  query: string;
  response: string;
  intent: string;
  risk_level: string;
  confidence: number;
  escalation_required: boolean;
  latency_ms: number;
  timestamp: string;
  traces?: any[];
}

export default function ChatPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const { ask } = await import("@/app/lib/api").then(m => ({ ask: m.api.ask }));
      const data = await ask(query);

      setQueryResponse({
        id: data.query,
        query: data.query,
        response: data.result.result,
        intent: data.intent.intent,
        risk_level: data.risk.risk_level,
        confidence: data.confidence_score || 0,
        escalation_required: data.escalate,
        latency_ms: data.latency_seconds * 1000,
        timestamp: new Date().toISOString(),
        traces: data.agent_details,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process query");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Policy Intelligence Chat</h1>
          <p className="text-gray-600 mt-2">Ask questions about retail policies</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChatWindow onQuery={handleQuery} isLoading={isLoading} />
          </div>

          <div className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">Error: {error}</p>
              </div>
            )}

            {isLoading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
                <Loader className="w-5 h-5 text-blue-600 animate-spin" />
                <p className="text-sm text-blue-800">Processing...</p>
              </div>
            )}

            {queryResponse && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Response</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-gray-600">Intent: {queryResponse.intent}</p>
                    <p className="text-gray-600">Risk: {queryResponse.risk_level}</p>
                    <p className="text-gray-600">Confidence: {(queryResponse.confidence * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
