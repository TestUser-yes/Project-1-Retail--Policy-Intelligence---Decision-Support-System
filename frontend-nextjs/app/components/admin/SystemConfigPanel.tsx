"use client";

import React, { useState } from "react";
import { Save, RotateCcw } from "lucide-react";
import { useSystemConfig } from "@/app/hooks/admin/useSystemConfig";

export function SystemConfigPanel() {
  const { configs, updateConfig, resetConfig } = useSystemConfig();
  const [savedMessage, setSavedMessage] = useState(false);

  const handleSave = (key: string, value: any) => {
    updateConfig(key, value);
    setSavedMessage(true);
    setTimeout(() => setSavedMessage(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          💡 System configuration controls SLO targets and platform behavior.
        </p>
      </div>

      {savedMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-green-800">✅ Configuration saved successfully</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config) => (
          <div key={config.key} className="bg-white rounded-lg shadow p-4">
            <div className="mb-3">
              <label className="block text-sm font-semibold text-gray-900 mb-1">
                {config.key.replace(/_/g, " ").toUpperCase()}
              </label>
              <p className="text-xs text-gray-600">{config.description}</p>
            </div>

            <div className="flex gap-2 items-end">
              {config.type === "boolean" ? (
                <select
                  value={String(config.value)}
                  onChange={(e) =>
                    handleSave(config.key, e.target.value === "true")
                  }
                  className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
                >
                  <option value="true">Enabled</option>
                  <option value="false">Disabled</option>
                </select>
              ) : (
                <input
                  type={config.type === "number" ? "number" : "text"}
                  defaultValue={String(config.value)}
                  onChange={(e) => {
                    const value = config.type === "number"
                      ? parseFloat(e.target.value)
                      : e.target.value;
                    handleSave(config.key, value);
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
                />
              )}

              <button
                onClick={() => resetConfig(config.key)}
                className="px-3 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-2">
              Last updated: {config.updatedAt.toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
