"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Loader, MoreVertical, Download, Trash2, MessageSquare } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: number;
  escalation_required?: boolean;
  risk_level?: string;
  timestamp: Date;
}

interface EnhancedChatWindowProps {
  onQuery?: (query: string) => void;
  isLoading?: boolean;
}

export function EnhancedChatWindow({ onQuery, isLoading = false }: EnhancedChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    onQuery?.(input);
    setInput("");
    setShowSuggestions(false);
  };

  const stats = {
    total_queries: messages.filter((m) => m.role === "user").length,
    avg_confidence: messages
      .filter((m) => m.confidence)
      .reduce((sum, m) => sum + (m.confidence || 0), 0) /
      messages.filter((m) => m.confidence).length || 0,
    high_risk_count: messages.filter((m) => m.risk_level === "high").length,
    escalation_count: messages.filter((m) => m.escalation_required).length,
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Stats Bar */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
        <div className="grid grid-cols-4 gap-3 text-xs">
          <div>
            <p className="text-gray-600">Queries</p>
            <p className="text-lg font-bold text-blue-600">{stats.total_queries}</p>
          </div>
          <div>
            <p className="text-gray-600">Avg Confidence</p>
            <p className="text-lg font-bold text-green-600">{(stats.avg_confidence * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-gray-600">High Risk</p>
            <p className="text-lg font-bold text-red-600">{stats.high_risk_count}</p>
          </div>
          <div>
            <p className="text-gray-600">Escalations</p>
            <p className="text-lg font-bold text-orange-600">{stats.escalation_count}</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">Start a conversation</p>
              <p className="text-gray-400 text-sm">Ask questions about policies</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white rounded-br-none"
                  : "bg-gray-100 text-gray-900 rounded-bl-none"
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              {msg.role === "assistant" && (
                <div className="mt-2 text-xs space-y-1">
                  {msg.confidence && (
                    <p className="opacity-75">Confidence: {(msg.confidence * 100).toFixed(0)}%</p>
                  )}
                  {msg.risk_level && (
                    <p className="opacity-75">Risk: {msg.risk_level}</p>
                  )}
                  {msg.escalation_required && (
                    <p className="text-red-300 font-semibold">⚠️ Escalation</p>
                  )}
                </div>
              )}
              <p className="text-xs opacity-50 mt-1">
                {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-lg rounded-bl-none">
              <Loader className="w-5 h-5 text-gray-500 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <div className="mb-3 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {messages.length > 0 && `${messages.filter((m) => m.role === "user").length} queries`}
          </div>
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-gray-100 rounded"
          >
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {showMenu && (
          <div className="mb-3 w-full bg-white border border-gray-200 rounded-lg shadow-lg">
            <button
              onClick={() => {
                const text = messages
                  .map((m) => `${m.role.toUpperCase()}: ${m.content}`)
                  .join("\n");
                const blob = new Blob([text], { type: "text/plain" });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `chat-${new Date().toISOString()}.txt`;
                a.click();
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export Chat
            </button>
            <button
              onClick={() => {
                setMessages([]);
                setShowMenu(false);
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2 text-red-600"
            >
              <Trash2 className="w-4 h-4" />
              Clear Chat
            </button>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a policy question..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 flex items-center gap-2 transition"
          >
            {isLoading ? <Loader className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
