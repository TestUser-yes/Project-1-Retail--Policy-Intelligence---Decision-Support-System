'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, RefreshCw, Filter } from 'lucide-react';

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<any[]>([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchEscalations();
  }, []);

  const fetchEscalations = async () => {
    setEscalations([
      {
        id: 1,
        query: 'Tell me a joke',
        reason: 'Out-of-scope',
        status: 'pending',
        submittedAt: '2026-07-03 14:23',
        submittedBy: 'John Doe',
        assignedTo: null,
      },
      {
        id: 2,
        query: 'Can we change vendor payment terms for restricted supplier?',
        reason: 'High-risk vendor decision',
        status: 'reviewed',
        submittedAt: '2026-07-03 13:45',
        submittedBy: 'Sarah Smith',
        assignedTo: 'Emily Chen',
      },
      {
        id: 3,
        query: 'Is it possible to bypass compliance check for expedited delivery?',
        reason: 'Compliance bypass request',
        status: 'pending',
        submittedAt: '2026-07-03 12:10',
        submittedBy: 'Mike Johnson',
        assignedTo: null,
      },
      {
        id: 4,
        query: 'What is our refund policy for B2B customers?',
        reason: 'Requires approval',
        status: 'resolved',
        submittedAt: '2026-07-02 16:00',
        submittedBy: 'Emily Chen',
        assignedTo: 'Sarah Smith',
      },
    ]);
  };

  const filteredEscalations = escalations.filter(e => filter === 'all' || e.status === filter);

  const getStatusIcon = (status: string) => {
    if (status === 'pending') return <Clock className="w-5 h-5 text-yellow-500" />;
    if (status === 'reviewed') return <AlertCircle className="w-5 h-5 text-blue-500" />;
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      pending: 'bg-yellow-100 text-yellow-800',
      reviewed: 'bg-blue-100 text-blue-800',
      resolved: 'bg-green-100 text-green-800',
    };
    return variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Escalation Queue</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          <RefreshCw className="w-5 h-5" />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <Filter className="w-5 h-5 text-gray-400" />
        <div className="flex gap-2">
          {['all', 'pending', 'reviewed', 'resolved'].map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg transition capitalize ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Escalations List */}
      <div className="space-y-4">
        {filteredEscalations.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">No escalations in this category</p>
          </div>
        ) : (
          filteredEscalations.map(esc => (
            <div key={esc.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition border-l-4 border-blue-600">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(esc.status)}
                    <h3 className="font-semibold text-gray-900 text-lg">{esc.query}</h3>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Reason: <strong>{esc.reason}</strong></span>
                    <span>By: <strong>{esc.submittedBy}</strong></span>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(esc.status)}`}>
                  {esc.status}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Submitted</p>
                  <p className="text-sm font-semibold text-gray-900">{esc.submittedAt}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Assigned To</p>
                  <p className="text-sm font-semibold text-gray-900">{esc.assignedTo || 'Unassigned'}</p>
                </div>
                <div className="flex items-end justify-end gap-2">
                  {esc.status === 'pending' && (
                    <>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
                        Review
                      </button>
                      <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm">
                        Assign
                      </button>
                    </>
                  )}
                  {esc.status === 'reviewed' && (
                    <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm">
                      Resolve
                    </button>
                  )}
                  {esc.status === 'resolved' && (
                    <span className="text-sm text-green-600 font-semibold">✓ Resolved</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">Queue Summary</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Pending</p>
            <p className="text-2xl font-bold text-yellow-600">{escalations.filter(e => e.status === 'pending').length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Reviewed</p>
            <p className="text-2xl font-bold text-blue-600">{escalations.filter(e => e.status === 'reviewed').length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Resolved</p>
            <p className="text-2xl font-bold text-green-600">{escalations.filter(e => e.status === 'resolved').length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-gray-900">{escalations.length}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
