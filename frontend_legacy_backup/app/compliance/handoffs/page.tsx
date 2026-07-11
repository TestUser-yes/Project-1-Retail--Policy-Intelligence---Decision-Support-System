'use client';

import { useState } from 'react';
import { AlertCircle, CheckCircle, Clock, FileText, User } from 'lucide-react';

export default function HandoffsPage() {
  const [handoffs] = useState([
    {
      id: 1,
      query: 'Tell me a joke',
      status: 'pending',
      submittedBy: 'John Doe',
      submittedAt: '2 hours ago',
      notes: 'User asked for a joke - completely out of scope',
      priority: 'low',
    },
    {
      id: 2,
      query: 'Can we change vendor payment terms for restricted supplier?',
      status: 'reviewing',
      submittedBy: 'Sarah Smith',
      submittedAt: '4 hours ago',
      notes: 'High-risk vendor decision. Requires compliance review and approval.',
      priority: 'high',
      resolution: 'Escalate to CFO for vendor policy review',
    },
    {
      id: 3,
      query: 'Is it possible to bypass compliance check for expedited delivery?',
      status: 'resolved',
      submittedBy: 'Mike Johnson',
      submittedAt: 'Yesterday',
      notes: 'Request to bypass compliance - security concern',
      priority: 'critical',
      resolution: 'Denied - Compliance controls must be maintained',
    },
  ]);

  const getStatusIcon = (status: string) => {
    if (status === 'pending') return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    if (status === 'reviewing') return <Clock className="w-5 h-5 text-blue-500" />;
    return <CheckCircle className="w-5 h-5 text-green-500" />;
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      high: 'bg-red-100 text-red-800',
      critical: 'bg-red-200 text-red-900',
    };
    return colors[priority as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Escalation Handoffs</h1>

      {/* Handoffs List */}
      <div className="space-y-4">
        {handoffs.map(handoff => (
          <div key={handoff.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition border-l-4 border-amber-600">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusIcon(handoff.status)}
                  <h3 className="font-semibold text-lg text-gray-900">{handoff.query}</h3>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <User className="w-4 h-4" />
                    <span>{handoff.submittedBy}</span>
                  </div>
                  <span>{handoff.submittedAt}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPriorityColor(handoff.priority)}`}>
                  {handoff.priority}
                </span>
                <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-xs font-semibold capitalize">
                  {handoff.status}
                </span>
              </div>
            </div>

            {/* Notes */}
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-2">
                <FileText className="w-5 h-5 text-gray-400 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900 mb-1">Handoff Notes</p>
                  <p className="text-sm text-gray-700">{handoff.notes}</p>
                </div>
              </div>
            </div>

            {/* Resolution (if exists) */}
            {handoff.resolution && (
              <div className="bg-green-50 rounded-lg p-4 mb-4 border border-green-200">
                <p className="text-sm font-semibold text-green-900 mb-1">Resolution</p>
                <p className="text-sm text-green-800">{handoff.resolution}</p>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2">
              {handoff.status === 'pending' && (
                <>
                  <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-semibold">
                    Reject
                  </button>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-semibold">
                    Start Review
                  </button>
                </>
              )}
              {handoff.status === 'reviewing' && (
                <>
                  <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-semibold">
                    Need More Info
                  </button>
                  <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-semibold">
                    Resolve
                  </button>
                </>
              )}
              {handoff.status === 'resolved' && (
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-semibold cursor-default">
                  ✓ Closed
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
