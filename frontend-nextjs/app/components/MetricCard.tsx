'use client';

import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon: ReactNode;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    percent: number;
  };
  status?: 'pass' | 'warning' | 'fail' | 'info';
  onClick?: () => void;
}

export default function MetricCard({
  label,
  value,
  unit,
  icon,
  trend,
  status = 'info',
  onClick,
}: MetricCardProps) {
  const statusColors = {
    pass: 'border-green-200 bg-green-50',
    warning: 'border-yellow-200 bg-yellow-50',
    fail: 'border-red-200 bg-red-50',
    info: 'border-blue-200 bg-blue-50',
  };

  const statusTextColors = {
    pass: 'text-green-700',
    warning: 'text-yellow-700',
    fail: 'text-red-700',
    info: 'text-blue-700',
  };

  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-400',
  };

  return (
    <div
      className={`p-6 rounded-lg border-2 ${statusColors[status]} transition-all hover:shadow-lg ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${statusTextColors[status]} bg-white`}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-semibold ${trendColors[trend.direction]}`}>
            {trend.direction === 'up' && <ArrowUpRight className="w-4 h-4" />}
            {trend.direction === 'down' && <ArrowDownRight className="w-4 h-4" />}
            {trend.direction === 'stable' && <Minus className="w-4 h-4" />}
            {trend.percent > 0 && `${trend.percent.toFixed(1)}%`}
          </div>
        )}
      </div>

      <p className="text-sm text-gray-600 font-medium mb-2">{label}</p>

      <div className="flex items-baseline gap-1">
        <span className={`text-3xl font-bold ${statusTextColors[status]}`}>{value}</span>
        {unit && <span className="text-sm text-gray-500">{unit}</span>}
      </div>
    </div>
  );
}
