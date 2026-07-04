"use client";

import { useState, useCallback } from "react";

export interface QuerySuggestion {
  text: string;
  category: "policy" | "vendor" | "compliance" | "escalation";
  frequency: number;
}

export function useSuggestions() {
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([
    {
      text: "What is the vendor approval policy?",
      category: "policy",
      frequency: 0,
    },
    {
      text: "List all critical vendors",
      category: "vendor",
      frequency: 0,
    },
    {
      text: "Show compliance status",
      category: "compliance",
      frequency: 0,
    },
    {
      text: "Get escalation status",
      category: "escalation",
      frequency: 0,
    },
  ]);

  // Filter suggestions based on query prefix
  const getFilteredSuggestions = useCallback(
    (query: string): QuerySuggestion[] => {
      if (!query.trim()) return suggestions.slice(0, 3);

      return suggestions.filter((s) =>
        s.text.toLowerCase().includes(query.toLowerCase())
      );
    },
    [suggestions]
  );

  // Track query usage for smarter suggestions
  const recordQueryUsage = useCallback((query: string) => {
    setSuggestions((prev) =>
      prev
        .map((s) => ({
          ...s,
          frequency: s.text.toLowerCase() === query.toLowerCase()
            ? s.frequency + 1
            : s.frequency,
        }))
        .sort((a, b) => b.frequency - a.frequency)
    );
  }, []);

  // Add custom suggestion
  const addSuggestion = useCallback(
    (text: string, category: QuerySuggestion["category"]) => {
      setSuggestions((prev) => [
        ...prev,
        { text, category, frequency: 0 },
      ]);
    },
    []
  );

  return {
    suggestions,
    getFilteredSuggestions,
    recordQueryUsage,
    addSuggestion,
  };
}
