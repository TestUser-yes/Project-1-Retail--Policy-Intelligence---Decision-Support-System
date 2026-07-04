"use client";

import { useState, useCallback } from "react";

export interface Filters {
  riskLevel?: "low" | "medium" | "high" | "all";
  dateRange?: {
    from: Date;
    to: Date;
  };
  searchQuery?: string;
  status?: "all" | "resolved" | "pending" | "escalated";
  agent?: string;
}

export function useFilters() {
  const [filters, setFilters] = useState<Filters>({
    riskLevel: "all",
    status: "all",
    searchQuery: "",
  });

  const updateFilter = useCallback((key: keyof Filters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const setDateRange = useCallback((from: Date, to: Date) => {
    setFilters((prev) => ({
      ...prev,
      dateRange: { from, to },
    }));
  }, []);

  const setSearchQuery = useCallback((query: string) => {
    setFilters((prev) => ({
      ...prev,
      searchQuery: query,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      riskLevel: "all",
      status: "all",
      searchQuery: "",
      dateRange: undefined,
    });
  }, []);

  const getActiveFilterCount = useCallback(() => {
    let count = 0;
    if (filters.riskLevel && filters.riskLevel !== "all") count++;
    if (filters.status && filters.status !== "all") count++;
    if (filters.searchQuery) count++;
    if (filters.dateRange) count++;
    if (filters.agent) count++;
    return count;
  }, [filters]);

  return {
    filters,
    updateFilter,
    setDateRange,
    setSearchQuery,
    resetFilters,
    getActiveFilterCount,
  };
}
