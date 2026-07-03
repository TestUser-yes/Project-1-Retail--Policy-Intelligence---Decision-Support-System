'use client';

import { useState } from 'react';
import { TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

export default function SLAMonitoringPage() {
  const [slaMetrics] = useState({
    target: 24, // hours
    breached: 1,
    atRisk: 3,
    compliant: 38,
    avgResolution: 2.75,
  });

  const cases = [
    {
      id: 1,
      query: 'Out-of-scope: Tell me a joke',
      submitted: '2 hours ago',
      deadline: '22h remaining',
      status: 'compliant',
      assignee: 'Sarah Smith',
    },
    {
      id: 2,
      query: 'High-risk: Vendor terms change',
      submitted: '4 hours ago',
      deadline: '20h remaining',
      status: 'compliant',
      assignee: 'Emily Chen',
    },
    {
      id: 3,
      query: 'Compliance: Bypass request',
      submitted: '20 hours ago',
      deadline: '4h remaining',
      status: 'at-risk',
      assignee: 'John Doe',
    },
    {
      id: 4,
      query: 'Policy interpretation question',
      submitted: '26 hours ago',
      deadline: 'Breached',
      status: 'breached',
      assignee: 'Unassigned',
    },
  ];

  const getStatusColor = (status: string) => {
    if (status === 'compliant') return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' };
    if (status === 'at-risk') return { icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' };
    return { icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' };
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">24-Hour SLA Monitoring</h1>

      {/* SLA Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Compliant</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{slaMetrics.compliant}</p>
              <p className="text-xs text-gray-500 mt-1">Within 24 hours</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">At Risk</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">{slaMetrics.atRisk}</p>
              <p className="text-xs text-gray-500 mt-1">&lt;4 hours remaining</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Breached</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{slaMetrics.breached}</p>
              <p className="text-xs text-gray-500 mt-1">SLA exceeded</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Avg Resolution</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{slaMetrics.avgResolution}h</p>
              <p className="text-xs text-gray-500 mt-1">Target: {slaMetrics.target}h</p>
            </div>
            <Clock className="w-12 h-12 text-blue-600" />
          </div>
        </div>
      </div>

      {/* SLA Compliance Rate */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Overall SLA Compliance</h2>
        <div className="relative pt-2">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">96.8% Compliant</span>
            <span className="text-sm text-gray-600">42/42 compliant cases</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div className="bg-gradient-to-r from-green-500 to-green-600 h-4 rounded-full" style={{ width: '96.8%' }}></div>
          </div>
          <p className="text-sm text-gray-600 mt-4">1 case breached SLA. Immediate action required for 3 at-risk cases.</p>
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Escalation Cases by SLA Status</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Query</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Submitted</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">SLA Deadline</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Assigned To</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {cases.map(caseItem => {
                const { icon: Icon, color, bg, border } = getStatusColor(caseItem.status);
                return (
                  <tr key={caseItem.id} className={`hover:${bg} transition`}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{caseItem.query}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{caseItem.submitted}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        caseItem.status === 'compliant' ? 'bg-green-100 text-green-800' :
                        caseItem.status === 'at-risk' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {caseItem.deadline}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-5 h-5 ${color}`} />
                        <span className="capitalize font-semibold text-gray-900">
                          {caseItem.status === 'at-risk' ? 'At Risk' : caseItem.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{caseItem.assignee}</td>
                    <td className="px-6 py-4 text-sm">
                      {caseItem.status === 'breached' && (
                        <button className="text-red-600 hover:text-red-900 font-semibold">⚠ Escalate</button>
                      )}
                      {caseItem.status === 'at-risk' && (
                        <button className="text-yellow-600 hover:text-yellow-900 font-semibold">⏱ Prioritize</button>
                      )}
                      {caseItem.status === 'compliant' && (
                        <span className="text-green-600 font-semibold">✓ On Track</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alerts */}
      <div className="space-y-4">
        <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded-r-lg">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-red-900">SLA Breach Alert</h3>
              <p className="text-sm text-red-800 mt-1">One case has exceeded the 24-hour SLA. Immediate manager review required.</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4 rounded-r-lg">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-yellow-900">At-Risk Cases</h3>
              <p className="text-sm text-yellow-800 mt-1">3 cases are at risk of breaching SLA (less than 4 hours remaining). Recommend prioritization.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
