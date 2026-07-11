'use client';

import { CheckCircle, AlertCircle, XCircle, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';

export interface HealthStatus {
  name: string;
  status: 'healthy' | 'warning' | 'down';
  lastChecked?: Date;
}

interface SystemHealthProps {
  onRefresh?: () => void;
}

export default function SystemHealth({ onRefresh }: SystemHealthProps) {
  const [statuses, setStatuses] = useState<HealthStatus[]>([
    { name: 'Backend API', status: 'healthy' },
    { name: 'Database', status: 'healthy' },
    { name: 'Langfuse Observability', status: 'healthy' },
    { name: 'Cache System', status: 'healthy' },
  ]);

  const [loading, setLoading] = useState(false);

  const handleRefresh = async () => {
    setLoading(true);
    // Simulate health check
    await new Promise(resolve => setTimeout(resolve, 1000));
    setStatuses(prev =>
      prev.map(s => ({
        ...s,
        lastChecked: new Date(),
      }))
    );
    setLoading(false);
    onRefresh?.();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'down':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return null;
    }
  };

  const healthyCount = statuses.filter(s => s.status === 'healthy').length;
  const allHealthy = healthyCount === statuses.length;

  return (
    <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">System Health</h3>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="p-2 hover:bg-gray-100 rounded-lg transition disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="mb-4 p-3 rounded-lg bg-slate-50 border border-slate-200">
        <div className="flex items-center gap-2">
          {allHealthy ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-yellow-600" />
          )}
          <span className="text-sm font-semibold text-gray-800">
            {healthyCount}/{statuses.length} components operational
          </span>
        </div>
      </div>

      <div className="space-y-2">
        {statuses.map(status => (
          <div
            key={status.name}
            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition"
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(status.status)}
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{status.name}</p>
                {status.lastChecked && (
                  <p className="text-xs text-gray-500">
                    Last checked: {status.lastChecked.toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
            <span
              className={`text-xs font-semibold px-2 py-1 rounded ${
                status.status === 'healthy'
                  ? 'bg-green-100 text-green-800'
                  : status.status === 'warning'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
