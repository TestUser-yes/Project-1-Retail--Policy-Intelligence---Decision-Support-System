"use client";

import { useState, useCallback, useEffect } from "react";

interface ConversationMessage {
  id: string;
  query: string;
  response: string;
  intent: string;
  risk_level: string;
  confidence: number;
  escalation_required: boolean;
  timestamp: Date;
  latency_ms: number;
}

export function useConversationHistory() {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load conversation history from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("conversation_history");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setMessages(parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })));
      } catch (error) {
        console.error("Failed to load conversation history:", error);
      }
    }
  }, []);

  // Save conversation history to localStorage
  const saveToLocalStorage = useCallback((msgs: ConversationMessage[]) => {
    localStorage.setItem("conversation_history", JSON.stringify(msgs));
  }, []);

  // Add message to history
  const addMessage = useCallback((message: ConversationMessage) => {
    setMessages((prev) => {
      const updated = [...prev, message];
      saveToLocalStorage(updated);
      return updated;
    });
  }, [saveToLocalStorage]);

  // Clear conversation history
  const clearHistory = useCallback(() => {
    setMessages([]);
    localStorage.removeItem("conversation_history");
  }, []);

  // Export conversation
  const exportConversation = useCallback(() => {
    const text = messages
      .map(
        (msg) =>
          `Q: ${msg.query}\nA: ${msg.response}\nConfidence: ${(msg.confidence * 100).toFixed(0)}%\n---\n`
      )
      .join("\n");

    const blob = new Blob([text], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `conversation-${new Date().toISOString()}.txt`;
    a.click();
  }, [messages]);

  // Get conversation stats
  const getStats = useCallback(() => {
    if (messages.length === 0) {
      return {
        total_queries: 0,
        avg_confidence: 0,
        high_risk_count: 0,
        escalation_count: 0,
        avg_latency: 0,
      };
    }

    return {
      total_queries: messages.length,
      avg_confidence:
        messages.reduce((sum, m) => sum + m.confidence, 0) / messages.length,
      high_risk_count: messages.filter((m) => m.risk_level === "high").length,
      escalation_count: messages.filter((m) => m.escalation_required).length,
      avg_latency:
        messages.reduce((sum, m) => sum + m.latency_ms, 0) / messages.length,
    };
  }, [messages]);

  return {
    messages,
    addMessage,
    clearHistory,
    exportConversation,
    getStats,
  };
}
