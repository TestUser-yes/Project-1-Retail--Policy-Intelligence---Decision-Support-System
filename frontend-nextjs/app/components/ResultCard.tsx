'use client';

import { useState } from 'react';
import { AskResponse } from '@/app/lib/api';
import {
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Zap,
  FileText,
  MapPin,
} from 'lucide-react';
import EscalationModal from './EscalationModal';

interface ResultCardProps {
  result: AskResponse;
}

export default function ResultCard({ result }: ResultCardProps) {
  const [showEscalationModal, setShowEscalationModal] = useState(false);
  const [handoffSubmitted, setHandoffSubmitted] = useState(false);

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-900',
          icon: 'text-red-600',
          badge: 'bg-red-100 text-red-800',
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-900',
          icon: 'text-yellow-600',
          badge: 'bg-yellow-100 text-yellow-800',
        };
      default:
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-900',
          icon: 'text-green-600',
          badge: 'bg-green-100 text-green-800',
        };
    }
  };

  const getSLOColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'pass':
        return {
          bg: 'bg-green-50',
          border: 'border-green-300',
          badge: 'bg-green-100 text-green-800',
          text: 'text-green-900',
        };
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-300',
          badge: 'bg-yellow-100 text-yellow-800',
          text: 'text-yellow-900',
        };
      case 'fail':
        return {
          bg: 'bg-red-50',
          border: 'border-red-300',
          badge: 'bg-red-100 text-red-800',
          text: 'text-red-900',
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-300',
          badge: 'bg-gray-100 text-gray-800',
          text: 'text-gray-900',
        };
    }
  };

  const riskColors = getRiskColor(result.risk?.risk_level);
  const sloColors = getSLOColor(result.slo_metrics?.slo_status);

  return (
    <div className="space-y-6">
      {/* Query Display */}
      <div className="card p-6 border-l-4 border-blue-600">
        <div className="flex gap-2 items-start">
          <FileText className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-600 uppercase">
              Your Query
            </p>
            <p className="text-lg text-gray-900 mt-2">{result.query}</p>
          </div>
        </div>
      </div>

      {/* Response */}
      <div className="card p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Response</h2>
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-lg">
            {result.result?.result || result.result}
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Route */}
        <div className="card p-6 hover:shadow-xl transition">
          <div className="flex items-center gap-2 mb-2">
            <MapPin className="w-5 h-5 text-blue-600" />
            <p className="text-sm font-semibold text-gray-600 uppercase">
              Route
            </p>
          </div>
          <p className="text-3xl font-bold text-blue-600">
            {result.route?.toUpperCase()}
          </p>
        </div>

        {/* Risk Level */}
        <div
          className={`card p-6 border-2 ${riskColors.border} hover:shadow-xl transition`}
        >
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className={`w-5 h-5 ${riskColors.icon}`} />
            <p className="text-sm font-semibold text-gray-600 uppercase">
              Risk Level
            </p>
          </div>
          <p className={`text-3xl font-bold ${riskColors.text}`}>
            {result.risk?.risk_level?.toUpperCase()}
          </p>
          <p className={`text-sm mt-2 ${riskColors.text} opacity-75`}>
            {result.risk?.reason}
          </p>
        </div>

        {/* Intent */}
        <div className="card p-6 hover:shadow-xl transition">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-purple-600" />
            <p className="text-sm font-semibold text-gray-600 uppercase">
              Intent
            </p>
          </div>
          <p className="text-2xl font-bold text-purple-600">
            {result.intent?.intent?.toUpperCase()}
          </p>
        </div>
      </div>

      {/* SLO Metrics */}
      {result.slo_metrics && (
        <div
          className={`card p-6 border-2 ${sloColors.border} hover:shadow-xl transition`}
        >
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-6 h-6 text-blue-600" />
            <h3 className="text-xl font-bold text-gray-900">SLO Metrics</h3>
            <span className={`ml-auto px-3 py-1 rounded-full text-sm font-semibold ${sloColors.badge}`}>
              {result.slo_metrics.slo_status?.toUpperCase()}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-xs font-semibold text-gray-600 uppercase">
                Actual Latency
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {result.slo_metrics.latency_ms?.toFixed(2)}ms
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-xs font-semibold text-gray-600 uppercase">
                Target Latency
              </p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {result.slo_metrics.target_latency_ms?.toFixed(0)}ms
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-xs font-semibold text-gray-600 uppercase">
                Performance
              </p>
              <p className={`text-3xl font-bold mt-2 ${sloColors.text}`}>
                {result.slo_metrics.slo_status?.charAt(0).toUpperCase() +
                  result.slo_metrics.slo_status?.slice(1)}
              </p>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 border-l-4 border-blue-600 rounded text-sm text-blue-900">
            <p className="font-semibold">Performance Insight</p>
            <p className="mt-1">
              {result.slo_metrics.slo_status === 'pass'
                ? '✓ Query processed within SLO target'
                : result.slo_metrics.slo_status === 'warning'
                ? '⚠ Query approaching SLO limit'
                : '✗ Query exceeded SLO target'}
            </p>
          </div>
        </div>
      )}

      {/* Cost & Budget */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="w-6 h-6 text-green-600" />
          <h3 className="text-xl font-bold text-gray-900">Cost & Budget</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600 font-semibold uppercase">
              Query Cost
            </p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              ${result.cost_usd?.toFixed(4)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-semibold uppercase">
              Budget Remaining
            </p>
            <p className="text-2xl font-bold text-blue-600 mt-2">
              ${result.budget_remaining_usd?.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 font-semibold uppercase">
              Budget Used
            </p>
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-500 to-blue-600"
                  style={{
                    width: `${Math.min(result.budget_percent_used, 100)}%`,
                  }}
                />
              </div>
              <p className="text-lg font-bold text-gray-900 min-w-fit">
                {result.budget_percent_used?.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Escalation Alert */}
      {result.escalate && (
        <div className="card p-6 border-2 border-red-300 bg-red-50">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-red-600 mt-1 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-xl font-bold text-red-900 mb-2">
                ⚠️ ESCALATION REQUIRED
              </h3>
              <p className="text-red-800 mb-4">
                {result.escalation_reason ||
                  'This query requires human review due to high risk or low confidence.'}
              </p>

              {!handoffSubmitted ? (
                <button
                  onClick={() => setShowEscalationModal(true)}
                  className="btn-danger"
                >
                  Handoff to Compliance Officer
                </button>
              ) : (
                <div className="flex items-center gap-2 text-green-600 font-semibold">
                  <CheckCircle className="w-5 h-5" />
                  <span>Handoff submitted successfully</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Escalation Modal */}
      {showEscalationModal && (
        <EscalationModal
          query={result.query}
          reason={result.escalation_reason}
          onConfirm={() => {
            setHandoffSubmitted(true);
            setShowEscalationModal(false);
          }}
          onCancel={() => setShowEscalationModal(false)}
        />
      )}
    </div>
  );
}
