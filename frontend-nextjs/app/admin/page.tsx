'use client';

import { useEffect, useState } from 'react';
import { Activity, Users, AlertTriangle, TrendingUp, BarChart3 } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalQueries: 0,
    escalations: 0,
    systemHealth: 'Checking...'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalUsers: 42,
          totalQueries: 1523,
          escalations: 87,
          systemHealth: data.status === 'healthy' ? 'Healthy' : 'Warning'
        });
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, color }: any) => (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
        </div>
        <Icon className={`w-12 h-12 ${color}`} />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold text-gray-900">Admin Dashboard</h1>
        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-semibold text-green-700">System {loading ? 'Loading' : stats.systemHealth}</span>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard icon={Users} title="Total Users" value={stats.totalUsers} color="text-blue-600" />
        <StatCard icon={BarChart3} title="Total Queries" value={stats.totalQueries} color="text-green-600" />
        <StatCard icon={AlertTriangle} title="Escalations" value={stats.escalations} color="text-red-600" />
        <StatCard icon={TrendingUp} title="Success Rate" value="94.2%" color="text-indigo-600" />
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-8">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Recent Activity</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-start gap-4 pb-4 border-b">
            <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-sm font-semibold text-gray-900">User john.doe logged in</p>
              <p className="text-xs text-gray-500 mt-1">2 minutes ago</p>
            </div>
          </div>
          <div className="flex items-start gap-4 pb-4 border-b">
            <div className="w-2 h-2 bg-red-600 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-sm font-semibold text-gray-900">Query escalated: Out-of-scope question</p>
              <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-2 h-2 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <p className="text-sm font-semibold text-gray-900">User sarah.smith submitted handoff</p>
              <p className="text-xs text-gray-500 mt-1">12 minutes ago</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Query Performance</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">Avg Response Time</span>
                <span className="text-sm font-semibold text-gray-900">245ms</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">SLO Compliance</span>
                <span className="text-sm font-semibold text-gray-900">98.5%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '98.5%' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">System Resources</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">CPU Usage</span>
                <span className="text-sm font-semibold text-gray-900">32%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '32%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-gray-700">Memory Usage</span>
                <span className="text-sm font-semibold text-gray-900">58%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '58%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
