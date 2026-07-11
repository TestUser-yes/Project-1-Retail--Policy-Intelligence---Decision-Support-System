"use client";

import { useState, useCallback } from "react";

export interface SystemConfig {
  key: string;
  value: string | number | boolean;
  description: string;
  type: "string" | "number" | "boolean";
  updatedAt: Date;
}

export function useSystemConfig() {
  const [configs, setConfigs] = useState<SystemConfig[]>([
    {
      key: "slo_target_success_rate",
      value: 90,
      description: "SLO target for success rate (%)",
      type: "number",
      updatedAt: new Date(),
    },
    {
      key: "slo_target_latency",
      value: 3000,
      description: "SLO target for P95 latency (ms)",
      type: "number",
      updatedAt: new Date(),
    },
    {
      key: "max_escalations_per_hour",
      value: 10,
      description: "Maximum escalations allowed per hour",
      type: "number",
      updatedAt: new Date(),
    },
    {
      key: "enable_auto_refresh",
      value: true,
      description: "Enable automatic dashboard refresh",
      type: "boolean",
      updatedAt: new Date(),
    },
  ]);

  const getConfig = useCallback((key: string) => {
    return configs.find((c) => c.key === key)?.value;
  }, [configs]);

  const updateConfig = useCallback((key: string, value: any) => {
    setConfigs((prev) =>
      prev.map((c) =>
        c.key === key ? { ...c, value, updatedAt: new Date() } : c
      )
    );
  }, []);

  const resetConfig = useCallback((key: string) => {
    // Reset to default (could fetch from backend)
    setConfigs((prev) =>
      prev.map((c) =>
        c.key === key ? { ...c, updatedAt: new Date() } : c
      )
    );
  }, []);

  return {
    configs,
    getConfig,
    updateConfig,
    resetConfig,
  };
}
