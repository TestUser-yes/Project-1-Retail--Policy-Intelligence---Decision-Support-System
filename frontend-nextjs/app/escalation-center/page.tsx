'use client';

import { useState, useMemo } from 'react';
import {
  AlertTriangle,
  Clock,
  Search,
  Filter,
  Plus,
  ChevronRight,
  MessageSquare,
  FileText,
  Code,
  Brain,
  CheckCircle,
  AlertCircle,
  Loader,
} from 'lucide-react';

interface EscalationCase {
  id: string;
  caseNumber: string;
  question: string;
  reason: string;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
  assignedTeam: string;
  status: 'pending' | 'in_review' | 'resolved' | 'rejected';
  createdAt: string;
  updatedAt: string;
  conversation: Array<{ role: string; message: string }>;
  policiesApplied: Array<{ policy: string; clause: string }>;
  sqlValidation: { query: string; status: string; result: any };
  reasoning: string;
}

const MOCK_CASES: EscalationCase[] = [
  {
    id: '1',
    caseNumber: 'E-1004',
    question: 'Delete customer data under legal hold',
    reason: 'Conflict between policy and request',
    risk: 'HIGH',
    confidence: 63,
    assignedTeam: 'Legal Team',
    status: 'pending',
    createdAt: '2026-01-15',
    updatedAt: '2026-01-15',
    conversation: [
      { role: 'user', message: 'Can we delete transaction records for customer ABC under legal hold?' },
      { role: 'assistant', message: 'This requires escalation due to legal hold flag and potential compliance conflict.' },
    ],
    policiesApplied: [
      { policy: 'Data Retention Policy', clause: '4.2' },
      { policy: 'GDPR', clause: 'Article 17 (Right to Erasure)' },
    ],
    sqlValidation: {
      query: 'SELECT * FROM retention_records WHERE legal_hold_flag = TRUE AND customer_id = "ABC"',
      status: 'executed',
      result: { rows_affected: 0, legal_hold: true, status: 'BLOCKED' },
    },
    reasoning: 'Legal hold status prevents erasure despite customer request. Requires legal review.',
  },
  {
    id: '2',
    caseNumber: 'E-1003',
    question: 'Approve ABC Logistics for new contracts',
    reason: 'High-risk vendor with open findings',
    risk: 'MEDIUM',
    confidence: 72,
    assignedTeam: 'Compliance Team',
    status: 'in_review',
    createdAt: '2026-01-12',
    updatedAt: '2026-01-18',
    conversation: [
      { role: 'user', message: 'Can we approve ABC Logistics for our 2026 supplier program?' },
      { role: 'assistant', message: 'ABC Logistics has risk_score of 82 with open audit findings. Requires compliance review.' },
    ],
    policiesApplied: [
      { policy: 'Supplier & Vendor Compliance Policy', clause: '3.1' },
      { policy: 'Anti-Bribery Policy', clause: '2.3' },
    ],
    sqlValidation: {
      query: 'SELECT vendor_id, risk_score, compliance_status FROM vendors WHERE vendor_name = "ABC Logistics"',
      status: 'executed',
      result: { vendor_id: 1, risk_score: 82, status: 'Under Review' },
    },
    reasoning: 'Vendor has high risk score but some compliant areas. Approval depends on remediation timeline.',
  },
  {
    id: '3',
    caseNumber: 'E-1002',
    question: 'Transfer employee data to EU jurisdiction',
    reason: 'Cross-border transfer with restricted jurisdiction',
    risk: 'HIGH',
    confidence: 91,
    assignedTeam: 'Legal Team',
    status: 'in_review',
    createdAt: '2026-01-10',
    updatedAt: '2026-01-17',
    conversation: [
      { role: 'user', message: 'Can we move HR records to our EU subsidiary?' },
      { role: 'assistant', message: 'GDPR compliance required. Need data processing agreement and adequacy assessment.' },
    ],
    policiesApplied: [
      { policy: 'Data Privacy Policy', clause: '5.2' },
      { policy: 'GDPR', clause: 'Chapter 5 (Transfers)' },
    ],
    sqlValidation: {
      query: 'SELECT COUNT(*) FROM employee_records WHERE jurisdiction = "US" AND data_class = "sensitive"',
      status: 'executed',
      result: { total_records: 1250, sensitive_records: 450 },
    },
    reasoning: 'High volume of sensitive data. Requires GDPR compliance verification and DPA agreement.',
  },
  {
    id: '4',
    caseNumber: 'E-1001',
    question: 'Override vendor rejection despite critical findings',
    reason: 'Business pressure vs policy requirements',
    risk: 'HIGH',
    confidence: 85,
    assignedTeam: 'Legal Team',
    status: 'resolved',
    createdAt: '2026-01-08',
    updatedAt: '2026-01-14',
    conversation: [
      { role: 'user', message: 'Can we override the rejection of vendor Prime Distribution?' },
      { role: 'assistant', message: 'Prime Distribution marked Non-Compliant with Critical risk. Override not recommended.' },
    ],
    policiesApplied: [
      { policy: 'Supplier & Vendor Compliance Policy', clause: '4.1' },
    ],
    sqlValidation: {
      query: 'SELECT vendor_id, risk_category, compliance_status FROM vendors WHERE vendor_name = "Prime Distribution"',
      status: 'executed',
      result: { vendor_id: 4, risk_category: 'Critical', status: 'Non-Compliant' },
    },
    reasoning: 'Critical findings require remediation before approval. Rejection upheld.',
  },
];

const TEAMS = ['All Teams', 'Legal Team', 'Compliance Team', 'Security Team', 'Finance Team'];
const STATUSES = ['All Statuses', 'pending', 'in_review', 'resolved', 'rejected'];

export default function EscalationCenter() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTeam, setSelectedTeam] = useState('All Teams');
  const [selectedStatus, setSelectedStatus] = useState('All Statuses');
  const [expandedCase, setExpandedCase] = useState<string | null>(null);

  const filteredCases = useMemo(() => {
    return MOCK_CASES.filter((caseItem) => {
      const matchesSearch =
        caseItem.caseNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        caseItem.question.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTeam = selectedTeam === 'All Teams' || caseItem.assignedTeam === selectedTeam;
      const matchesStatus = selectedStatus === 'All Statuses' || caseItem.status === selectedStatus;
      return matchesSearch && matchesTeam && matchesStatus;
    });
  }, [searchTerm, selectedTeam, selectedStatus]);

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'HIGH':
        return { bg: 'bg-red-50', border: 'border-red-300', badge: 'bg-red-100 text-red-800', text: 'text-red-700' };
      case 'MEDIUM':
        return { bg: 'bg-yellow-50', border: 'border-yellow-300', badge: 'bg-yellow-100 text-yellow-800', text: 'text-yellow-700' };
      default:
        return { bg: 'bg-green-50', border: 'border-green-300', badge: 'bg-green-100 text-green-800', text: 'text-green-700' };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'in_review':
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
      case 'resolved':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Escalation Center</h1>
              <p className="text-gray-600 mt-2">
                Manage high-risk compliance cases and human escalations
              </p>
            </div>
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center gap-2 transition">
              <Plus className="w-5 h-5" />
              New Case
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by case ID or question..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-2 block">Assigned Team</label>
              <div className="flex flex-wrap gap-2">
                {TEAMS.map((team) => (
                  <button
                    key={team}
                    onClick={() => setSelectedTeam(team)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                      selectedTeam === team
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {team}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-700 mb-2 block">Status</label>
              <div className="flex flex-wrap gap-2">
                {STATUSES.map((status) => (
                  <button
                    key={status}
                    onClick={() => setSelectedStatus(status)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                      selectedStatus === status
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Found <span className="font-bold text-gray-900">{filteredCases.length}</span> case{filteredCases.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {/* Cases List */}
        <div className="space-y-4">
          {filteredCases.map((caseItem) => {
            const riskColor = getRiskColor(caseItem.risk);
            const isExpanded = expandedCase === caseItem.id;

            return (
              <div
                key={caseItem.id}
                className={`bg-white rounded-lg border-2 transition ${
                  isExpanded ? 'border-blue-400 shadow-lg' : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                {/* Case Header */}
                <button
                  onClick={() => setExpandedCase(isExpanded ? null : caseItem.id)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition"
                >
                  <div className="flex items-start gap-4 flex-1 text-left">
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(caseItem.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-bold text-gray-900">Case {caseItem.caseNumber}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-bold ${riskColor.badge}`}>
                          {caseItem.risk}
                        </span>
                        <span className="px-2 py-1 rounded text-xs font-bold bg-gray-100 text-gray-800">
                          {caseItem.status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-gray-700 line-clamp-2 mb-2">{caseItem.question}</p>
                      <div className="flex flex-wrap gap-4 text-xs text-gray-600">
                        <span>Confidence: <span className="font-semibold">{caseItem.confidence}%</span></span>
                        <span>Assigned: <span className="font-semibold">{caseItem.assignedTeam}</span></span>
                        <span>Created: {caseItem.createdAt}</span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight
                    className={`w-5 h-5 text-gray-400 transition transform ${isExpanded ? 'rotate-90' : ''}`}
                  />
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t-2 border-slate-200 bg-slate-50">
                    {/* Tab Navigation */}
                    <div className="flex border-b border-slate-200 bg-white px-6">
                      {[
                        { id: 'details', label: 'Details', icon: FileText },
                        { id: 'conversation', label: 'Conversation', icon: MessageSquare },
                        { id: 'policies', label: 'Policies', icon: FileText },
                        { id: 'sql', label: 'SQL', icon: Code },
                        { id: 'reasoning', label: 'Reasoning', icon: Brain },
                      ].map(({ id, label, icon: Icon }) => (
                        <button
                          key={id}
                          className="flex items-center gap-2 px-4 py-3 text-sm font-semibold text-gray-700 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-600 transition"
                        >
                          <Icon className="w-4 h-4" />
                          {label}
                        </button>
                      ))}
                    </div>

                    <div className="p-6 space-y-6">
                      {/* Details Tab */}
                      <div>
                        <h4 className="font-bold text-gray-900 mb-4">Case Details</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <p className="text-xs font-bold text-gray-600 uppercase">Confidence</p>
                            <p className="text-2xl font-bold text-blue-600 mt-2">{caseItem.confidence}%</p>
                          </div>
                          <div className={`${riskColor.bg} border ${riskColor.border} rounded-lg p-3`}>
                            <p className="text-xs font-bold text-gray-600 uppercase">Risk</p>
                            <p className={`text-2xl font-bold ${riskColor.text} mt-2`}>{caseItem.risk}</p>
                          </div>
                          <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <p className="text-xs font-bold text-gray-600 uppercase">Team</p>
                            <p className="text-sm font-bold text-gray-900 mt-2">{caseItem.assignedTeam}</p>
                          </div>
                          <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <p className="text-xs font-bold text-gray-600 uppercase">Status</p>
                            <p className="text-sm font-bold text-gray-900 mt-2 capitalize">{caseItem.status.replace('_', ' ')}</p>
                          </div>
                        </div>

                        <div className="mt-4 bg-white border border-gray-200 rounded-lg p-4">
                          <p className="text-xs font-bold text-gray-600 uppercase mb-2">Reason for Escalation</p>
                          <p className="text-gray-800">{caseItem.reason}</p>
                        </div>
                      </div>

                      {/* Conversation */}
                      <div>
                        <h4 className="font-bold text-gray-900 mb-4">Conversation History</h4>
                        <div className="space-y-3">
                          {caseItem.conversation.map((msg, idx) => (
                            <div
                              key={idx}
                              className={`p-3 rounded-lg ${
                                msg.role === 'user'
                                  ? 'bg-blue-50 border border-blue-200'
                                  : 'bg-gray-100 border border-gray-200'
                              }`}
                            >
                              <p className="text-xs font-bold text-gray-600 uppercase mb-1">
                                {msg.role === 'user' ? 'User' : 'Assistant'}
                              </p>
                              <p className="text-sm text-gray-800">{msg.message}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Policies */}
                      <div>
                        <h4 className="font-bold text-gray-900 mb-4">Policies Applied</h4>
                        <div className="space-y-2">
                          {caseItem.policiesApplied.map((policy, idx) => (
                            <div
                              key={idx}
                              className="flex items-start gap-2 p-3 bg-white border border-gray-200 rounded-lg"
                            >
                              <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="font-semibold text-gray-900">{policy.policy}</p>
                                <p className="text-xs text-gray-600">Clause {policy.clause}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* SQL Validation */}
                      <div>
                        <h4 className="font-bold text-gray-900 mb-4">SQL Validation</h4>
                        <div className="space-y-2">
                          <div>
                            <p className="text-xs font-bold text-gray-600 uppercase mb-2">Query</p>
                            <pre className="bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto text-xs font-mono border border-gray-700">
                              {caseItem.sqlValidation.query}
                            </pre>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-gray-600 uppercase">Status:</span>
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">
                              {caseItem.sqlValidation.status.toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <p className="text-xs font-bold text-gray-600 uppercase mb-2">Result</p>
                            <pre className="bg-white border border-gray-300 p-3 rounded-lg overflow-x-auto text-xs font-mono max-h-48">
                              {JSON.stringify(caseItem.sqlValidation.result, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </div>

                      {/* Reasoning */}
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <p className="text-xs font-bold text-indigo-900 uppercase mb-2">Agent Reasoning</p>
                        <p className="text-sm text-indigo-900">{caseItem.reasoning}</p>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-3 pt-4 border-t border-slate-300">
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold text-sm transition">
                          Change Status
                        </button>
                        <button className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 font-semibold text-sm transition">
                          Reassign
                        </button>
                        <button className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 font-semibold text-sm transition">
                          Add Note
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {filteredCases.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border-2 border-slate-200">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No cases found</h3>
            <p className="text-gray-600">Try adjusting your filters or create a new case</p>
          </div>
        )}
      </div>
    </div>
  );
}
