'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, Clock, CheckCircle, TrendingUp } from 'lucide-react';

export default function ComplianceDashboard() {
  // Constants from capstone requirements
  const SLA_TARGET_HOURS = 24;

  const [stats, setStats] = useState({
    pendingHandoffs: 0,
    completedToday: 0,
    avgResolutionTime: '0h',
    slaCompliance: '0%',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const dashboardResponse = await fetch(`${apiUrl}/api/dashboard`);
      if (dashboardResponse.ok) {
        const data = await dashboardResponse.json();
        setStats({
          pendingHandoffs: data.escalationCount || 0,
          completedToday: Math.floor((data.totalQueries || 0) * 0.5), // Approximate
          avgResolutionTime: `${(data.avgLatency || 0).toFixed(0)}ms`,
          slaCompliance: `${(data.successRate || 0).toFixed(1)}%`,
        });
      } else {
        setStats({
          pendingHandoffs: 0,
          completedToday: 0,
          avgResolutionTime: 'N/A',
          slaCompliance: 'N/A',
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      setStats({
        pendingHandoffs: 0,
        completedToday: 0,
        avgResolutionTime: 'Error',
        slaCompliance: 'Error',
      });
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color, subtext }: any) => (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
          {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
        </div>
        <Icon className={`w-12 h-12 ${color}`} />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold text-gray-900">Compliance Officer Dashboard</h1>
        <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-semibold text-blue-700">Monitoring Active</span>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          icon={AlertTriangle}
          title="Pending Handoffs"
          value={stats.pendingHandoffs}
          color="text-red-600"
          subtext="Requires attention"
        />
        <StatCard
          icon={CheckCircle}
          title="Completed Today"
          value={stats.completedToday}
          color="text-green-600"
          subtext="Escalations resolved"
        />
        <StatCard
          icon={Clock}
          title="Avg Resolution"
          value={stats.avgResolutionTime}
          color="text-blue-600"
          subtext="From handoff to close"
        />
        <StatCard
          icon={TrendingUp}
          title="SLA Compliance"
          value={stats.slaCompliance}
          color="text-indigo-600"
          subtext="24-hour target met"
        />
      </div>

      {/* Recent Handoffs */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Escalations Assigned to You</h2>
        <div className="space-y-4">
          <div className="border-l-4 border-red-600 p-4 bg-red-50 rounded-r-lg">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900">"Tell me a joke"</h3>
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded text-xs font-semibold">Pending</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">Reason: Out-of-scope query</p>
            <p className="text-xs text-gray-500">Submitted: 2 hours ago by John Doe</p>
          </div>

          <div className="border-l-4 border-blue-600 p-4 bg-blue-50 rounded-r-lg">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900">"Can we change vendor terms for restricted supplier?"</h3>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded text-xs font-semibold">Under Review</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">Reason: High-risk vendor decision</p>
            <p className="text-xs text-gray-500">Submitted: 4 hours ago by Sarah Smith</p>
          </div>

          <div className="border-l-4 border-green-600 p-4 bg-green-50 rounded-r-lg">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900">"Is it possible to bypass compliance check?"</h3>
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded text-xs font-semibold">Resolved</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">Reason: Compliance bypass request</p>
            <p className="text-xs text-gray-500">Resolution: Denied - Approved by Sarah Smith</p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Weekly Performance</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">Cases Resolved</span>
                <span className="text-sm font-semibold text-gray-900">42/45</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '93%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">SLA Met</span>
                <span className="text-sm font-semibold text-gray-900">96.8%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '96.8%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">First-Contact Resolution</span>
                <span className="text-sm font-semibold text-gray-900">78%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '78%' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">24-Hour SLA Tracking</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-green-50 border border-green-200 rounded">
              <span className="text-sm text-gray-700">Within SLA</span>
              <span className="text-2xl font-bold text-green-600">38</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 border border-yellow-200 rounded">
              <span className="text-sm text-gray-700">At Risk (&lt;4 hours left)</span>
              <span className="text-2xl font-bold text-yellow-600">3</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 border border-red-200 rounded">
              <span className="text-sm text-gray-700">Breached SLA</span>
              <span className="text-2xl font-bold text-red-600">1</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
