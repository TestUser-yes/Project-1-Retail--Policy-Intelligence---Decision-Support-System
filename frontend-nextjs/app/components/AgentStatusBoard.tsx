"use client";

import React from "react";
import { Activity, AlertCircle, CheckCircle, Clock } from "lucide-react";

interface Agent {
  name: string;
  status: "active" | "inactive" | "error";
  last_used?: string;
  latency_avg_ms?: number;
  success_rate?: number;
  traces_count?: number;
}

interface AgentStatusBoardProps {
  agents: Agent[];
}

export function AgentStatusBoard({ agents }: AgentStatusBoardProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-50 border-green-200";
      case "error":
        return "bg-red-50 border-red-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  const agentGroups = {
    "Core Agents": [
      "IntentAgent",
      "RiskAgent",
      "RouterAgent",
    ],
    "Execution Agents": [
      "RetrievalAgent",
      "SQLAgent",
      "PolicyAgent",
    ],
    "Validation Agents": [
      "ComplianceAgent",
      "ValidatorAgent",
      "ReflectionAgent",
    ],
    "Output Agents": [
      "ConfidenceAgent",
      "ResponseAgent",
      "EscalationAgent",
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Activity className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
      </div>

      {Object.entries(agentGroups).map(([group, agentNames]) => (
        <div key={group}>
          <h4 className="text-sm font-semibold text-gray-700 mb-2">{group}</h4>
          <div className="grid grid-cols-1 gap-2">
            {agentNames.map((agentName) => {
              const agent = agents.find((a) => a.name === agentName) || {
                name: agentName,
                status: "inactive" as const,
              };

              return (
                <div key={agent.name} className={`border rounded-lg p-3 ${getStatusBg(agent.status)}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(agent.status)}
                      <div className="flex-1">
                        <p className="font-medium text-sm text-gray-900">{agent.name}</p>
                        {agent.last_used && (
                          <p className="text-xs text-gray-600">
                            Last used: {new Date(agent.last_used).toLocaleTimeString()}
                          </p>
                        )}
                      </div>
                    </div>
                    {agent.success_rate && (
                      <div className="text-right">
                        <p className="text-xs font-semibold text-gray-700">
                          {agent.success_rate.toFixed(0)}%
                        </p>
                        <p className="text-xs text-gray-600">{agent.latency_avg_ms?.toFixed(0)}ms</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
