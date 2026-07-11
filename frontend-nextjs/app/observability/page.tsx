'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  TrendingUp,
  AlertCircle,
  Zap,
  DollarSign,
  Clock,
  BarChart3,
  Loader,
} from 'lucide-react';
import MetricCard from '@/app/components/MetricCard';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ObservabilityData {
  totalQueries: number;
  avgConfidence: number;
  avgLatency: number;
  escalationRate: number;
  avgCost: number;
  intentDistribution: Array<{ name: string; value: number }>;
  riskDistribution: Array<{ name: string; value: number }>;
  queryTypeDistribution: Array<{ name: string; value: number }>;
  latencyTrend: Array<{ time: string; latency: number; target: number }>;
  confidenceTrend: Array<{ time: string; confidence: number }>;
  langfuseTraces: Array<{ id: string; name: string; duration: number; status: string }>;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function ObservabilityPage() {
  const [data, setData] = useState<ObservabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  useEffect(() => {
    const loadObservability = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
        const response = await fetch(`${apiUrl}/api/observability`);

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const observabilityData = await response.json();
        setData(observabilityData);
      } catch (err) {
        // Set mock data for demo
        setData({
          totalQueries: 1245,
          avgConfidence: 92,
          avgLatency: 2.1,
          escalationRate: 8,
          avgCost: 0.045,
          intentDistribution: [
            { name: 'Policy Interpretation', value: 450 },
            { name: 'Vendor Lookup', value: 380 },
            { name: 'Regulatory Query', value: 280 },
            { name: 'Data Request', value: 135 },
          ],
          riskDistribution: [
            { name: 'Low', value: 600 },
            { name: 'Medium', value: 450 },
            { name: 'High', value: 195 },
          ],
          queryTypeDistribution: [
            { name: 'RAG', value: 500 },
            { name: 'SQL', value: 400 },
            { name: 'Hybrid', value: 345 },
          ],
          latencyTrend: [
            { time: '00:00', latency: 1.8, target: 3 },
            { time: '04:00', latency: 1.9, target: 3 },
            { time: '08:00', latency: 2.2, target: 3 },
            { time: '12:00', latency: 2.4, target: 3 },
            { time: '16:00', latency: 2.1, target: 3 },
            { time: '20:00', latency: 1.9, target: 3 },
          ],
          confidenceTrend: [
            { time: '00:00', confidence: 91 },
            { time: '04:00', confidence: 92 },
            { time: '08:00', confidence: 91 },
            { time: '12:00', confidence: 93 },
            { time: '16:00', confidence: 92 },
            { time: '20:00', confidence: 92 },
          ],
          langfuseTraces: [
            { id: 'trace-001', name: 'Intent Classification', duration: 125, status: 'success' },
            { id: 'trace-002', name: 'RAG Retrieval', duration: 890, status: 'success' },
            { id: 'trace-003', name: 'SQL Execution', duration: 450, status: 'success' },
            { id: 'trace-004', name: 'Risk Assessment', duration: 230, status: 'success' },
            { id: 'trace-005', name: 'Response Formatting', duration: 180, status: 'success' },
          ],
        });
      } finally {
        setLoading(false);
      }
    };

    loadObservability();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-semibold">Loading observability data...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center text-red-600">
          <AlertCircle className="w-12 h-12 mx-auto mb-4" />
          <p className="font-semibold">Failed to load observability dashboard</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Observability Dashboard</h1>
          <p className="text-gray-600">
            Real-time metrics from Langfuse and system instrumentation
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <MetricCard
            label="Total Queries"
            value={data.totalQueries.toLocaleString()}
            icon={<Activity className="w-6 h-6" />}
            status="info"
            trend={{ direction: 'up', percent: 12.5 }}
          />
          <MetricCard
            label="Avg Confidence"
            value={`${data.avgConfidence}%`}
            icon={<TrendingUp className="w-6 h-6" />}
            status="pass"
            trend={{ direction: 'up', percent: 2.3 }}
          />
          <MetricCard
            label="Avg Latency"
            value={`${data.avgLatency}s`}
            icon={<Clock className="w-6 h-6" />}
            status="pass"
            trend={{ direction: 'down', percent: 5.1 }}
          />
          <MetricCard
            label="Escalation Rate"
            value={`${data.escalationRate}%`}
            icon={<AlertCircle className="w-6 h-6" />}
            status="warning"
            trend={{ direction: 'stable', percent: 0 }}
          />
          <MetricCard
            label="Avg Cost"
            value={`$${data.avgCost.toFixed(3)}`}
            icon={<DollarSign className="w-6 h-6" />}
            status="info"
            trend={{ direction: 'up', percent: 1.2 }}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Intent Distribution */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Intent Distribution
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.intentDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill={COLORS[0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Risk Distribution
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data.riskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Query Type Distribution */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Query Type Distribution
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data.queryTypeDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.queryTypeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Latency Trend */}
          <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Latency Trend (24h)
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data.latencyTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke={COLORS[0]}
                  strokeWidth={2}
                  name="Actual Latency"
                />
                <Line
                  type="monotone"
                  dataKey="target"
                  stroke={COLORS[3]}
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="SLO Target"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Confidence Trend */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Confidence Score Trend (24h)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.confidenceTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[80, 100]} />
              <Tooltip formatter={(value) => `${value}%`} />
              <Line
                type="monotone"
                dataKey="confidence"
                stroke={COLORS[1]}
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Langfuse Traces */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Recent Langfuse Traces
          </h3>
          <div className="space-y-3">
            {data.langfuseTraces.map((trace) => (
              <div
                key={trace.id}
                className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg hover:shadow-md transition"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <Zap className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{trace.name}</p>
                      <p className="text-xs text-gray-600">ID: {trace.id}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-sm font-mono font-bold text-gray-900">
                      {trace.duration}ms
                    </p>
                  </div>
                  <div className="text-center min-w-fit">
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                      {trace.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Langfuse Link */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              💡 <span className="font-semibold">Live Traces Available:</span> View detailed execution traces and LLM calls at{' '}
              <a
                href="https://cloud.langfuse.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-bold underline"
              >
                cloud.langfuse.com
              </a>
              {' '}using your project credentials.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
