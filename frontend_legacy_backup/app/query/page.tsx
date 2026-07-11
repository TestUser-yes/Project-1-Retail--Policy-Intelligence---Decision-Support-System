'use client';

import { useState } from 'react';
import QueryForm from '@/app/components/QueryForm';
import ResponseFormatter from '@/app/components/ResponseFormatter';
import { AskResponse } from '@/app/lib/api';

export default function QueryPage() {
  const [result, setResult] = useState<AskResponse | null>(null);
  const [conversationId, setConversationId] = useState<string>('');
  const [showEscalationModal, setShowEscalationModal] = useState(false);

  const handleResult = (newResult: AskResponse) => {
    setResult(newResult);
    setConversationId(newResult.conversation_id);
  };

  const handleEscalate = () => {
    setShowEscalationModal(true);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Retail Policy Intelligence Assistant
        </h1>
        <p className="text-gray-600">
          Ask compliance and policy questions and get structured, attributed answers
        </p>
      </div>

      <div className="space-y-8">
        {/* Query Form */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-8">
          <QueryForm onResult={handleResult} conversationId={conversationId} />
        </div>

        {/* Response Formatter */}
        {result && (
          <div>
            <ResponseFormatter result={result} onEscalate={handleEscalate} />
          </div>
        )}
      </div>
    </div>
  );
}
