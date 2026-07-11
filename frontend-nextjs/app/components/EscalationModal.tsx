'use client';

import { useState } from 'react';
import { AlertCircle, MessageSquare, Clock } from 'lucide-react';

interface EscalationModalProps {
  query: string;
  reason: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function EscalationModal({
  query,
  reason,
  onConfirm,
  onCancel,
}: EscalationModalProps) {
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const handoffData = {
        query,
        escalation_reason: reason,
        notes,
        timestamp: new Date().toISOString(),
        handoff_id: `HO-${Date.now()}`,
      };

      // TODO: Send to backend endpoint when ready
      // await api.submitHandoff(handoffData);

      onConfirm();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-in">
          <div className="flex items-center gap-3 mb-6">
            <AlertCircle className="w-8 h-8 text-red-600" />
            <h2 className="text-2xl font-bold text-gray-900">
              Handoff to Compliance Officer
            </h2>
          </div>

          <div className="space-y-6">
            {/* Escalation Reason */}
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
              <p className="text-sm font-semibold text-gray-700 mb-1">
                Escalation Reason
              </p>
              <p className="text-gray-900 font-medium">{reason}</p>
            </div>

            {/* Original Query */}
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-2">
                Original Query
              </p>
              <p className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900 border border-gray-200 truncate">
                "{query}"
              </p>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add context or notes for the compliance officer..."
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 resize-none"
                rows={4}
                disabled={submitting}
              />
              <p className="text-xs text-gray-500 mt-1">
                {notes.length} characters
              </p>
            </div>

            {/* What Happens Next */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
              <p className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                What Happens Next
              </p>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>✓ Compliance officer will be notified immediately</li>
                <li>✓ Query will be reviewed within 24 hours</li>
                <li>✓ You can track status in conversation history</li>
              </ul>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 mt-8">
            <button
              onClick={onCancel}
              disabled={submitting}
              className="flex-1 btn-secondary py-3 text-base"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex-1 btn-primary py-3 text-base"
            >
              {submitting ? 'Submitting...' : 'Confirm Handoff'}
            </button>
          </div>

          {/* Handoff ID Info */}
          <p className="text-xs text-gray-500 text-center mt-4">
            Handoff ID: HO-{Date.now()}
          </p>
        </div>
      </div>
    </>
  );
}
