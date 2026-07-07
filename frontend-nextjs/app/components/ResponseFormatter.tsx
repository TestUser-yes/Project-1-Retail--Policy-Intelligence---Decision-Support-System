'use client';

import { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Zap,
  FileText,
  MapPin,
  Target,
  BarChart3,
  Database,
  FileCheck,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { AskResponse } from '@/app/lib/api';

interface ResponseFormatterProps {
  result: AskResponse;
  onEscalate?: () => void;
}

export default function ResponseFormatter({ result, onEscalate }: ResponseFormatterProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    sources: true,
    sqlValidation: true,
    reasoning: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Risk color mapping
  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-red-50',
          border: 'border-red-300',
          text: 'text-red-900',
          badge: 'bg-red-100 text-red-800',
          icon: 'text-red-600',
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-300',
          text: 'text-yellow-900',
          badge: 'bg-yellow-100 text-yellow-800',
          icon: 'text-yellow-600',
        };
      default:
        return {
          bg: 'bg-green-50',
          border: 'border-green-300',
          text: 'text-green-900',
          badge: 'bg-green-100 text-green-800',
          icon: 'text-green-600',
        };
    }
  };

  // Confidence color mapping
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const riskColor = getRiskColor(result.risk?.risk_level);
  const confidenceColor = getConfidenceColor((result.confidence_score as any) ?? 0);

  return (
    <div className="space-y-6">
      {/* Question Display */}
      <div className="bg-white rounded-lg border-2 border-blue-200 p-6">
        <div className="flex gap-3 items-start">
          <FileText className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wide mb-2">
              Your Question
            </p>
            <p className="text-lg font-semibold text-gray-900">{result.query}</p>
          </div>
        </div>
      </div>

      {/* Answer Section */}
      <div className="bg-white rounded-lg border-2 border-slate-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">ANSWER</h2>
        <div className="bg-slate-50 p-6 rounded-lg border border-slate-300">
          <p className="text-base leading-relaxed text-gray-800 whitespace-pre-wrap">
            {typeof result.result === 'string' ? result.result : result.result?.result}
          </p>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Confidence */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-5 h-5 text-blue-600" />
            <span className="text-xs font-bold text-gray-600 uppercase">Confidence</span>
          </div>
          <div className="flex items-baseline gap-2">
            <p className={`text-3xl font-bold ${confidenceColor}`}>
              {(((result.confidence_score as any) ?? 0) * 100).toFixed(0)}%
            </p>
          </div>
          <div className="mt-3 w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                ((result.confidence_score as any) ?? 0) * 100 >= 90
                  ? 'bg-green-500'
                  : ((result.confidence_score as any) ?? 0) * 100 >= 70
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${((result.confidence_score as any) ?? 0) * 100}%` }}
            />
          </div>
        </div>

        {/* Risk Level */}
        <div
          className={`bg-white rounded-lg border-2 ${riskColor.border} p-4`}
        >
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className={`w-5 h-5 ${riskColor.icon}`} />
            <span className="text-xs font-bold text-gray-600 uppercase">Risk Level</span>
          </div>
          <p className={`text-3xl font-bold ${riskColor.text}`}>
            {result.risk?.risk_level?.toUpperCase()}
          </p>
          {result.risk?.reason && (
            <p className={`text-xs mt-2 ${riskColor.text} opacity-75`}>
              {result.risk.reason}
            </p>
          )}
        </div>

        {/* Retrieval Mode */}
        <div className="bg-white rounded-lg border-2 border-purple-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="w-5 h-5 text-purple-600" />
            <span className="text-xs font-bold text-gray-600 uppercase">Retrieval Mode</span>
          </div>
          <p className="text-2xl font-bold text-purple-600">
            {result.route?.toUpperCase() || 'HYBRID'}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {result.route === 'rag'
              ? 'Policy & Knowledge Base'
              : result.route === 'sql'
              ? 'Structured Database'
              : 'Combined Retrieval'}
          </p>
        </div>

        {/* Need Review */}
        <div className="bg-white rounded-lg border-2 border-amber-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <FileCheck className="w-5 h-5 text-amber-600" />
            <span className="text-xs font-bold text-gray-600 uppercase">Human Review</span>
          </div>
          <p className={`text-2xl font-bold ${result.escalate ? 'text-red-600' : 'text-green-600'}`}>
            {result.escalate ? 'YES' : 'NO'}
          </p>
          {result.escalation_reason && (
            <p className="text-xs text-gray-500 mt-2 line-clamp-2">
              {result.escalation_reason}
            </p>
          )}
        </div>
      </div>

      {/* Policy Sources Section */}
      <div className="bg-white rounded-lg border-2 border-slate-200 overflow-hidden">
        <button
          onClick={() => toggleSection('sources')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition"
        >
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-bold text-gray-900">POLICY SOURCES</h3>
          </div>
          {expandedSections.sources ? (
            <ChevronUp className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSections.sources && (
          <div className="border-t-2 border-slate-200 px-6 py-4 bg-slate-50">
            {(result.sources as any)?.length > 0 ? (
              <div className="space-y-3">
                {(result.sources as any).map((source: any, idx: number) => (
                  <div
                    key={idx}
                    className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-sm font-bold text-blue-600">{idx + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 text-sm">
                          {typeof source === 'string' ? source : source.document || source.source || source.policy || 'Unknown Source'}
                        </p>
                        {typeof source === 'object' && source.section && (
                          <p className="text-xs text-gray-600 mt-1">
                            Section: {source.section}
                          </p>
                        )}
                        {typeof source === 'object' && source.page && (
                          <p className="text-xs text-gray-600">
                            Page {source.page}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No specific policy sources cited</p>
            )}
          </div>
        )}
      </div>

      {/* SQL Validation Section */}
      <div className="bg-white rounded-lg border-2 border-slate-200 overflow-hidden">
        <button
          onClick={() => toggleSection('sqlValidation')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition"
        >
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-bold text-gray-900">SQL VALIDATION</h3>
          </div>
          {expandedSections.sqlValidation ? (
            <ChevronUp className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSections.sqlValidation && (
          <div className="border-t-2 border-slate-200 px-6 py-4 bg-slate-50">
            {(result.sql_validation as any) ? (
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-bold text-gray-600 uppercase mb-2">Query</p>
                  <pre className="bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto text-xs font-mono border border-gray-700">
                    {typeof (result.sql_validation as any) === 'string'
                      ? (result.sql_validation as any)
                      : (result.sql_validation as any).query || 'No query generated'}
                  </pre>
                </div>
                {typeof (result.sql_validation as any) === 'object' && (result.sql_validation as any).status && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-gray-600 uppercase">Status:</span>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      (result.sql_validation as any).status === 'executed' || (result.sql_validation as any).status === 'success'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {(result.sql_validation as any).status.toUpperCase()}
                    </span>
                  </div>
                )}
                {typeof (result.sql_validation as any) === 'object' && (result.sql_validation as any).result && (
                  <div>
                    <p className="text-xs font-bold text-gray-600 uppercase mb-2">Result</p>
                    <pre className="bg-white border border-gray-300 p-3 rounded-lg overflow-x-auto text-xs font-mono max-h-48">
                      {JSON.stringify((result.sql_validation as any).result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-600 text-sm">No SQL query was used for this response</p>
            )}
          </div>
        )}
      </div>

      {/* Recommendation Section */}
      <div className="bg-white rounded-lg border-2 border-slate-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-5 h-5 text-amber-600" />
          <h3 className="text-lg font-bold text-gray-900">RECOMMENDATION</h3>
        </div>
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
          <p className="text-gray-800 font-medium">
            {result.recommendation ||
              'Review the analysis above and consult with relevant stakeholders before taking action.'}
          </p>
        </div>
      </div>

      {/* Reasoning/Reflection Section */}
      <div className="bg-white rounded-lg border-2 border-slate-200 overflow-hidden">
        <button
          onClick={() => toggleSection('reasoning')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition"
        >
          <div className="flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-indigo-600" />
            <h3 className="text-lg font-bold text-gray-900">REASONING & REFLECTION</h3>
          </div>
          {expandedSections.reasoning ? (
            <ChevronUp className="w-5 h-5 text-gray-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600" />
          )}
        </button>

        {expandedSections.reasoning && (
          <div className="border-t-2 border-slate-200 px-6 py-4 bg-slate-50">
            <div className="space-y-3 text-sm text-gray-700">
              <div>
                <p className="font-semibold text-gray-900 mb-2">Processing Steps:</p>
                <ol className="list-decimal list-inside space-y-1 text-gray-700">
                  <li>Intent classification: {result.intent?.intent || 'Analysis'}</li>
                  <li>Retrieval mode: {result.route?.toUpperCase() || 'HYBRID'}</li>
                  <li>Risk assessment: {result.risk?.risk_level || 'MEDIUM'}</li>
                  <li>Confidence scoring: {((result.confidence_score ?? 0) * 100).toFixed(1)}%</li>
                  <li>Escalation evaluation: {result.escalate ? 'Required' : 'Not required'}</li>
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Escalation Alert */}
      {result.escalate && (
        <div className="bg-red-50 rounded-lg border-2 border-red-300 p-6">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-red-600 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-900 mb-2">
                ⚠️ ESCALATION REQUIRED
              </h3>
              <p className="text-red-800 mb-4">
                {result.escalation_reason ||
                  'This query requires human review due to high risk or low confidence.'}
              </p>
              {onEscalate && (
                <button
                  onClick={onEscalate}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition"
                >
                  Escalate to Compliance Officer
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-blue-50 border-l-4 border-blue-600 rounded-lg p-4">
        <p className="text-xs text-blue-900 leading-relaxed">
          <span className="font-bold">Important Note:</span> This system is intended to assist policy and compliance teams by providing explainable insights and structured retrieval. It does not replace legal or regulatory professionals. High-risk or ambiguous queries must trigger human review workflows.
        </p>
      </div>
    </div>
  );
}
