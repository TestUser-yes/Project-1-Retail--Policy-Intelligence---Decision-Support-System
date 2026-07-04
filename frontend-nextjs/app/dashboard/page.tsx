'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Zap,
  DollarSign,
  Clock,
  Activity,
  FileText,
  ArrowRight,
  Loader,
} from 'lucide-react';
import MetricCard from '@/app/components/MetricCard';
import SystemHealth from '@/app/components/SystemHealth';
import { formatCurrency, formatMilliseconds, formatNumber } from '@/app/lib/formatting';
import { generatePieChartData, COLORS } from '@/app/lib/charts';
import {
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { api } from '@/app/lib/api';

interface DashboardData {
  totalQueries: number;
  avgLatency: number;
  escalationRate: number;
  budgetUsed: number;
  budgetUsdLimit?: number;
  budgetUsdUsed?: number;
  activeUsers: number;
  successRate: number;
  queryByRoute: Record<string, number>;
  queryByRisk: Record<string, number>;
  topPolicies: Array<{ name: string; count: number }>;
  recentQueries: Array<{
    id: string;
    query: string;
    route: string;
    risk: string;
    cost: number;
    latency: number;
    timestamp: Date;
  }>;
  hourlyTrends: Array<{ time: string; queries: number; latency: number }>;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Fix hydration error - only render after hydration
  useEffect(() => {
    setHydrated(true);
  }, []);

  // Load initial dashboard data
  useEffect(() => {
    const loadDashboard = async () => {
      try {
        // Fetch real dashboard data from backend API
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/dashboard`);
        if (!response.ok) {
          throw new Error(`Dashboard API error: ${response.status}`);
        }

        const dashboardData = await response.json();

        // Transform backend response to frontend format
        const formattedData: DashboardData = {
          totalQueries: dashboardData.totalQueries || 0,
          avgLatency: dashboardData.avgLatency || 0,
          escalationRate: dashboardData.escalationRate || 0,
          budgetUsed: dashboardData.budgetUsed || 0,
          activeUsers: dashboardData.activeUsers || 0,
          successRate: dashboardData.successRate || 100,
          queryByRoute: dashboardData.queryByRoute || { rag: 0, sql: 0, hybrid: 0 },
          queryByRisk: dashboardData.queryByRisk || { low: 0, medium: 0, high: 0 },
          topPolicies: dashboardData.topPolicies || [],
          recentQueries: (dashboardData.recentQueries || []).map((q: any) => ({
            id: q.id || 'unknown',
            query: q.query || '',
            route: q.route || 'RAG',
            risk: q.risk || 'Unknown',
            cost: q.cost || 0,
            latency: q.latency || 0,
            timestamp: q.timestamp ? new Date(q.timestamp) : new Date(),
          })),
          hourlyTrends: dashboardData.hourlyTrends || [],
        };

        setData(formattedData);
        setError(null);
      } catch (err) {
        setError(`Failed to load dashboard data: ${err instanceof Error ? err.message : 'Unknown error'}`);
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  // Prevent rendering until hydration
  if (!hydrated || loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-semibold">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <p className="font-semibold">{error || 'Failed to load dashboard'}</p>
        </div>
      </div>
    );
  }

  // Generate chart data from real data
  const queryDistData = generatePieChartData(data.queryByRoute);
  const riskDistData = generatePieChartData(data.queryByRisk);

  const QUERY_COLORS = [COLORS.primary, COLORS.success, COLORS.warning];
  const RISK_COLORS = [COLORS.success, COLORS.warning, COLORS.danger];

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Retail Policy Intelligence System</h1>
          <p className="text-gray-600">SLO-Bound Autonomous Agentic AI Decision Support Dashboard</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8 flex flex-wrap gap-3">
          <Link
            href="/query"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition inline-flex items-center gap-2"
          >
            <Zap className="w-5 h-5" />
            Ask Question
          </Link>
          <Link
            href="/api-docs"
            className="px-6 py-3 bg-slate-200 text-gray-900 rounded-lg hover:bg-slate-300 font-semibold transition inline-flex items-center gap-2"
          >
            <FileText className="w-5 h-5" />
            API Documentation
          </Link>
          <Link
            href="/admin"
            className="px-6 py-3 border-2 border-gray-300 text-gray-900 rounded-lg hover:bg-gray-50 font-semibold transition inline-flex items-center gap-2"
          >
            <BarChart3 className="w-5 h-5" />
            Admin Panel
          </Link>
          <Link
            href="/compliance"
            className="px-6 py-3 border-2 border-amber-300 text-amber-900 rounded-lg hover:bg-amber-50 font-semibold transition inline-flex items-center gap-2"
          >
            <AlertTriangle className="w-5 h-5" />
            Compliance
          </Link>
        </div>

        {/* Real-time Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <MetricCard
            label="Total Queries"
            value={formatNumber(data.totalQueries)}
            icon={<Activity className="w-6 h-6" />}
            status="info"
            trend={{ direction: 'up', percent: 12.5 }}
          />
          <MetricCard
            label="Avg Response Time"
            value={formatMilliseconds(data.avgLatency * 1000)}
            icon={<Clock className="w-6 h-6" />}
            status="pass"
            trend={{ direction: 'down', percent: 8.2 }}
          />
          <MetricCard
            label="Escalation Rate"
            value={`${data.escalationRate}%`}
            icon={<AlertTriangle className="w-6 h-6" />}
            status="warning"
            trend={{ direction: 'stable', percent: 0 }}
          />
          <MetricCard
            label="Budget Used"
            value={`${data.budgetUsed}%`}
            unit="of $100/day"
            icon={<DollarSign className="w-6 h-6" />}
            status="info"
            trend={{ direction: 'up', percent: 3.5 }}
          />
        </div>

        {/* System Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg border-2 border-blue-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-2xl font-bold text-blue-600">{data.activeUsers}</span>
            </div>
            <p className="text-sm text-gray-600 font-medium">Active Users</p>
            <p className="text-xs text-gray-500 mt-2">Current session</p>
          </div>

          <div className="bg-white rounded-lg border-2 border-green-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-green-50 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-2xl font-bold text-green-600">{data.successRate}%</span>
            </div>
            <p className="text-sm text-gray-600 font-medium">Success Rate</p>
            <p className="text-xs text-gray-500 mt-2">SLO compliance</p>
          </div>

          <div className="bg-white rounded-lg border-2 border-emerald-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-50 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-emerald-600" />
              </div>
              <span className="text-2xl font-bold text-emerald-600">{formatCurrency(data.budgetUsed)}</span>
            </div>
            <p className="text-sm text-gray-600 font-medium">Budget Used</p>
            <p className="text-xs text-gray-500 mt-2">Daily budget: ${(data.budgetUsdLimit || 100).toFixed(2)}</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Query Distribution */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Query Routes</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={queryDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {queryDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={QUERY_COLORS[index % QUERY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatNumber(value as number)} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {queryDistData.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: QUERY_COLORS[idx] }}
                  />
                  <span className="text-gray-600">
                    {item.name}: {item.value} queries
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={riskDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={RISK_COLORS[index % RISK_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatNumber(value as number)} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {riskDistData.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: RISK_COLORS[idx] }}
                  />
                  <span className="text-gray-600">
                    {item.name}: {item.value} queries
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* System Health */}
          <SystemHealth />
        </div>

        {/* Query Trends */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Query Trends (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.hourlyTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="queries"
                stroke={COLORS.primary}
                strokeWidth={2}
                name="Queries"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="latency"
                stroke={COLORS.warning}
                strokeWidth={2}
                name="Avg Latency (s)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Policies */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Top Policies</h3>
          <div className="space-y-3">
            {data.topPolicies.map((policy, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-blue-600 w-6">{idx + 1}.</span>
                  <span className="text-sm font-medium text-gray-900">{policy.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-gray-600">{policy.count}</span>
                  <span className="text-xs text-gray-500">queries</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Queries */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Recent Queries</h3>
            <Link href="/query" className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1">
              Submit Query <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b-2 border-slate-200">
                <tr>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Query</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Route</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Risk</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Latency</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Cost</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Time</th>
                </tr>
              </thead>
              <tbody>
                {data.recentQueries.map((query, idx) => (
                  <tr key={idx} className="border-b border-slate-200 hover:bg-slate-50">
                    <td className="py-3 px-4 text-gray-900 max-w-xs truncate">{query.query}</td>
                    <td className="py-3 px-4">
                      <span className="text-xs font-bold px-2 py-1 rounded bg-blue-100 text-blue-800">
                        {query.route}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded ${
                          query.risk === 'Low'
                            ? 'bg-green-100 text-green-800'
                            : query.risk === 'Medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {query.risk}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-700 font-mono">{query.latency.toFixed(2)}s</td>
                    <td className="py-3 px-4 text-gray-700">{formatCurrency(query.cost)}</td>
                    <td className="py-3 px-4 text-gray-600 text-xs">
                      {query.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
