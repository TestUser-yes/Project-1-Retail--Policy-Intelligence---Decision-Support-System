import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { queryAPI } from '../services/api';

export default function QueryForm({ onSubmit, onResult }) {
  const [query, setQuery] = useState('');
  const { mutate, isPending, error } = useMutation({
    mutationFn: queryAPI.ask,
    onSuccess: (data) => {
      onSubmit(query);
      onResult(data);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      mutate(query);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8 min-h-[calc(100vh-200px)]">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Policy Query</h1>
        <p className="text-gray-600">Ask questions about policies, vendors, and compliance</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-700 mb-3">Your Question</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your policy question here..."
            className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 transition resize-none"
            rows="5"
          />
        </div>

        <button
          type="submit"
          disabled={isPending || !query.trim()}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold transition transform hover:scale-105 active:scale-95"
        >
          {isPending ? 'Processing...' : 'Submit Query'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded text-red-900 mb-8">
          <p className="font-bold">Error</p>
          <p>{error.message}</p>
        </div>
      )}

      {isPending && (
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Processing query...</p>
        </div>
      )}
    </div>
  );
}
