'use client';

import { useState } from 'react';
import { api, AskResponse } from '@/app/lib/api';
import { Loader, Send } from 'lucide-react';

interface QueryFormProps {
  onResult: (result: AskResponse) => void;
  conversationId?: string;
}

export default function QueryForm({ onResult, conversationId }: QueryFormProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.ask(query, conversationId);
      onResult(response);
      setQuery('');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          'Failed to process query'
      );
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Ask a Question About Retail Policies or Vendors
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Example: "What is our return policy?" or "Which vendors have best pricing?"'
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-600 resize-none"
            rows={4}
            disabled={loading}
          />
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-600 text-red-900 rounded">
            <p className="font-semibold">Error</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full btn-primary flex items-center justify-center gap-2 py-3 text-lg"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Submit Query
            </>
          )}
        </button>
      </form>
    </div>
  );
}
