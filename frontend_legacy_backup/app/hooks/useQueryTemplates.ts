"use client";

import { useState, useCallback } from "react";

export interface QueryTemplate {
  id: string;
  name: string;
  query: string;
  category: string;
  description: string;
  parameters?: {
    name: string;
    type: "string" | "date" | "number";
    placeholder?: string;
  }[];
  createdAt: Date;
  usageCount: number;
}

export function useQueryTemplates() {
  const [templates, setTemplates] = useState<QueryTemplate[]>([
    {
      id: "1",
      name: "Vendor Approval Policy",
      query: "What is the vendor approval policy?",
      category: "vendor",
      description: "Get information about vendor approval requirements",
      createdAt: new Date(),
      usageCount: 0,
    },
    {
      id: "2",
      name: "Compliance Status",
      query: "Show current compliance status",
      category: "compliance",
      description: "Check system compliance metrics",
      createdAt: new Date(),
      usageCount: 0,
    },
  ]);

  const addTemplate = useCallback(
    (template: Omit<QueryTemplate, "id" | "createdAt" | "usageCount">) => {
      const newTemplate: QueryTemplate = {
        ...template,
        id: Date.now().toString(),
        createdAt: new Date(),
        usageCount: 0,
      };
      setTemplates((prev) => [...prev, newTemplate]);
      return newTemplate;
    },
    []
  );

  const deleteTemplate = useCallback((id: string) => {
    setTemplates((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const useTemplate = useCallback((id: string) => {
    setTemplates((prev) =>
      prev.map((t) =>
        t.id === id ? { ...t, usageCount: t.usageCount + 1 } : t
      )
    );

    const template = templates.find((t) => t.id === id);
    return template?.query || "";
  }, [templates]);

  const getTemplatesByCategory = useCallback(
    (category: string) => templates.filter((t) => t.category === category),
    [templates]
  );

  return {
    templates,
    addTemplate,
    deleteTemplate,
    useTemplate,
    getTemplatesByCategory,
  };
}
