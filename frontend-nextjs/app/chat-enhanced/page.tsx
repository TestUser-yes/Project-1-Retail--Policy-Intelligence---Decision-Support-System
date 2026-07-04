"use client";

import React, { useState } from "react";
import { EnhancedChatWindow } from "@/app/components/EnhancedChatWindow";
import { Loader, Bookmark, BookmarkCheck } from "lucide-react";
import { queryStorage, type SavedQuery } from "@/app/utils/queryStorage";

export default function EnhancedChatPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [queryResponse, setQueryResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [showSavedQueries, setShowSavedQueries] = useState(false);
  const [saveQueryTitle, setSaveQueryTitle] = useState("");
  const [lastQuery, setLastQuery] = useState("");

  const handleQuery = async (query: string) => {
    setLastQuery(query);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/chat/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, user_id: "demo-user" }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setQueryResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process query");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveQuery = () => {
    if (saveQueryTitle && lastQuery) {
      const saved = queryStorage.saveQuery(saveQueryTitle, lastQuery, "general");
      setSavedQueries((prev) => [...prev, saved]);
      setSaveQueryTitle("");
    }
  };

  const handleLoadSavedQuery = (query: string) => {
    handleQuery(query);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Enhanced Chat</h1>
          <p className="text-gray-600 mt-2">Advanced policy intelligence with saved queries</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chat Window */}
          <div className="lg:col-span-2">
            <EnhancedChatWindow onQuery={handleQuery} isLoading={isLoading} />
          </div>

          {/* Side Panel */}
          <div className="space-y-4">
            {/* Save Query Section */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Save Query</h3>
              {lastQuery && (
                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Query title..."
                    value={saveQueryTitle}
                    onChange={(e) => setSaveQueryTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                  />
                  <button
                    onClick={handleSaveQuery}
                    className="w-full px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                  >
                    Save Query
                  </button>
                </div>
              )}
              {!lastQuery && (
                <p className="text-sm text-gray-500">Execute a query to save it</p>
              )}
            </div>

            {/* Saved Queries */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <button
                onClick={() => setShowSavedQueries(!showSavedQueries)}
                className="w-full flex items-center justify-between font-semibold text-gray-900"
              >
                <span>Saved Queries ({savedQueries.length})</span>
                <Bookmark className="w-5 h-5" />
              </button>

              {showSavedQueries && (
                <div className="mt-3 space-y-2">
                  {savedQueries.length === 0 ? (
                    <p className="text-sm text-gray-500">No saved queries yet</p>
                  ) : (
                    savedQueries.map((sq) => (
                      <button
                        key={sq.id}
                        onClick={() => handleLoadSavedQuery(sq.query)}
                        className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-blue-50 rounded text-sm text-gray-700 border border-gray-200 transition"
                      >
                        {sq.title}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* Response Details */}
            {queryResponse && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Response</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-gray-600">Intent</p>
                    <p className="font-medium text-gray-900">{queryResponse.intent}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Risk Level</p>
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${
                        queryResponse.risk_level === "high"
                          ? "bg-red-100 text-red-800"
                          : queryResponse.risk_level === "medium"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-green-100 text-green-800"
                      }`}
                    >
                      {queryResponse.risk_level.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-gray-600">Confidence</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{ width: `${queryResponse.confidence * 100}%` }}
                        />
                      </div>
                      <p className="font-medium text-gray-900 w-12 text-right">
                        {(queryResponse.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  {queryResponse.escalation_required && (
                    <div className="bg-red-50 border border-red-200 rounded p-2">
                      <p className="text-red-800 font-semibold text-xs">⚠️ Escalation Required</p>
                    </div>
                  )}
                </div>
              </div>
            )}

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
          </div>
        </div>
      </div>
    </div>
  );
}
