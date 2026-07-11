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
        // Step 1: Get demo token (sets secure httpOnly cookies on backend)
        await api.getToken();

        // Step 2: Verify that cookies were set and authentication works
        const authStatus = await api.checkAuthStatus();
        if (authStatus.authenticated) {
          setAuthenticated(true);
          setAuthError('');
        } else {
          setAuthError('Authentication check failed: ' + authStatus.message);
          setAuthenticated(false);
        }
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || err.message || 'Failed to authenticate';
        setAuthError('Authentication failed: ' + errorMsg);
        setAuthenticated(false);
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      {authError && (
        <div className="mb-4 p-4 bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-600 text-red-900 rounded-lg shadow-sm">
          <div className="flex items-start gap-3">
            <div className="p-1 bg-red-100 rounded-full flex-shrink-0 mt-0.5">
              <AlertCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="font-semibold">Authentication Error</p>
              <p className="text-sm mt-1">{authError}</p>
            </div>
          </div>
        </div>
      )}

      {authenticated && !authError && (
        <div className="mb-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-600 text-green-900 rounded-lg flex items-center gap-3 shadow-sm">
          <div className="p-1 bg-green-100 rounded-full">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <span className="font-semibold">Authenticated and ready ✓</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-3">
            Ask a Question About Retail Policies or Vendors
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Example: "What is our return policy?" or "Which vendors have best pricing?"'
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition bg-gray-50 hover:bg-white"
            rows={5}
            disabled={loading || !authenticated}
          />
          <p className="text-xs text-gray-500 mt-2">Minimum 3 characters, maximum 10,000 characters</p>
        </div>

        {error && (
          <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-600 text-red-900 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <div className="p-1 bg-red-100 rounded-full flex-shrink-0 mt-0.5">
                <AlertCircle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="font-semibold">Query Error</p>
                <p className="text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !query.trim() || !authenticated}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition duration-200 shadow-lg hover:shadow-xl disabled:shadow-none"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Processing Query...</span>
            </>
          ) : !authenticated ? (
            <>
              <AlertCircle className="w-5 h-5" />
              <span>Authenticating...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Submit Query</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
