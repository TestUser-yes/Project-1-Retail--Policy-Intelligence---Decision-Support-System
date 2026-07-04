'use client';

import { useState, useEffect } from 'react';
import { api, AskResponse } from '@/app/lib/api';
import { Loader, Send, AlertCircle, CheckCircle } from 'lucide-react';

interface QueryFormProps {
  onResult: (result: AskResponse) => void;
  conversationId?: string;
}

export default function QueryForm({ onResult, conversationId }: QueryFormProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          const response = await api.getToken();
          localStorage.setItem('access_token', response.access_token);
          setAuthenticated(true);
          setAuthError('');
        } else {
          setAuthenticated(true);
          setAuthError('');
        }
      } catch (err: any) {
        setAuthError('Failed to authenticate. Please refresh the page.');
        console.error('Auth error:', err);
      }
    };
    initAuth();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    if (!authenticated) {
      setError('Not authenticated. Please refresh the page.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.ask(query, conversationId);
      onResult(response);
      setQuery('');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to process query';
      setError(errorMsg);
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      {authError && (
        <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-600 text-red-900 rounded">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Authentication Error</p>
              <p className="text-sm mt-1">{authError}</p>
            </div>
          </div>
        </div>
      )}

      {authenticated && !authError && (
        <div className="mb-4 p-3 bg-green-50 border-l-4 border-green-600 text-green-900 rounded flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          <span className="text-sm">Authenticated and ready ✓</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Ask a Question About Retail Policies or Vendors
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Example: "What is our return policy?" or "Which vendors have best pricing?"'
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-600 resize-none transition"
            rows={4}
            disabled={loading || !authenticated}
          />
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-l-4 border-red-600 text-red-900 rounded">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold">Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !query.trim() || !authenticated}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing Query...
            </>
          ) : !authenticated ? (
            <>
              <AlertCircle className="w-5 h-5" />
              Authenticating...
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
