'use client';

import { useState } from 'react';
import QueryForm from '@/app/components/QueryForm';
import ResultCard from '@/app/components/ResultCard';
import { AskResponse } from '@/app/lib/api';

export default function QueryPage() {
  const [result, setResult] = useState<AskResponse | null>(null);
  const [conversationId, setConversationId] = useState<string>('');

  const handleResult = (newResult: AskResponse) => {
    setResult(newResult);
    setConversationId(newResult.conversation_id);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Ask a Question</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-3">
          <div className="card p-8">
            <QueryForm onResult={handleResult} conversationId={conversationId} />
          </div>
        </div>

        {result && (
          <div className="lg:col-span-3">
            <ResultCard result={result} />
          </div>
        )}
      </div>
    </div>
  );
}
