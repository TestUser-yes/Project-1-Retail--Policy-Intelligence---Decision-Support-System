'use client';

import { useState, useMemo } from 'react';
import { Search, Filter, Download, Eye, Book, Calendar, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface Policy {
  id: string;
  title: string;
  category: string;
  version: string;
  effectiveDate: string;
  sections: number;
  clauses: number;
  status: 'active' | 'archived' | 'draft';
  description: string;
  lastUpdated: string;
}

const POLICIES: Policy[] = [
  {
    id: 'data-privacy',
    title: 'Retail Data Protection & Customer Privacy Policy',
    category: 'Data Protection',
    version: '3.2',
    effectiveDate: '2025-01-01',
    lastUpdated: '2025-06-15',
    sections: 8,
    clauses: 24,
    status: 'active',
    description: 'Covers customer PII handling, consent management, data sharing restrictions, data breach obligations, and cross-border data transfer rules.',
  },
  {
    id: 'data-retention',
    title: 'Data Retention & Archival Policy',
    category: 'Records Management',
    version: '2.1',
    effectiveDate: '2024-06-01',
    lastUpdated: '2025-03-20',
    sections: 6,
    clauses: 18,
    status: 'active',
    description: 'Defines retention schedules by data category, deletion workflows, legal hold exceptions, and archival requirements.',
  },
  {
    id: 'supplier-compliance',
    title: 'Supplier & Vendor Compliance Policy',
    category: 'Vendor Management',
    version: '2.5',
    effectiveDate: '2024-09-01',
    lastUpdated: '2025-05-10',
    sections: 9,
    clauses: 27,
    status: 'active',
    description: 'Outlines vendor onboarding due diligence, risk classification model, ongoing compliance checks, and contractual obligations.',
  },
  {
    id: 'anti-bribery',
    title: 'Anti-Bribery & Ethical Conduct Policy',
    category: 'Compliance & Ethics',
    version: '1.8',
    effectiveDate: '2023-12-01',
    lastUpdated: '2025-04-05',
    sections: 7,
    clauses: 21,
    status: 'active',
    description: 'Covers gifts & hospitality rules, facilitation payments, conflict of interest disclosure, and whistleblower protections.',
  },
  {
    id: 'information-security',
    title: 'Information Security & Access Control Policy',
    category: 'Security',
    version: '4.1',
    effectiveDate: '2025-02-01',
    lastUpdated: '2025-06-10',
    sections: 10,
    clauses: 32,
    status: 'active',
    description: 'Defines access provisioning, role-based access control, MFA requirements, privileged account audits, and incident response triggers.',
  },
  {
    id: 'gdpr',
    title: 'GDPR Selected Articles (Excerpt)',
    category: 'Regulatory Framework',
    version: '2025',
    effectiveDate: '2018-05-25',
    lastUpdated: '2025-01-01',
    sections: 4,
    clauses: 12,
    status: 'active',
    description: 'Key GDPR provisions including Article 5 (Principles), Article 6 (Lawfulness), Article 17 (Right to Erasure), and Article 32 (Security).',
  },
  {
    id: 'iso-27001',
    title: 'ISO 27001 Access Control Summary',
    category: 'Information Security Standard',
    version: '2022',
    effectiveDate: '2022-10-01',
    lastUpdated: '2024-12-15',
    sections: 3,
    clauses: 8,
    status: 'active',
    description: 'Access control objectives, access review cadence, logging requirements, and security audit protocols.',
  },
];

const CATEGORIES = [
  'All Categories',
  'Data Protection',
  'Records Management',
  'Vendor Management',
  'Compliance & Ethics',
  'Security',
  'Regulatory Framework',
  'Information Security Standard',
];

export default function PolicyExplorer() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [expandedPolicy, setExpandedPolicy] = useState<string | null>(null);

  const filteredPolicies = useMemo(() => {
    return POLICIES.filter((policy) => {
      const matchesSearch =
        policy.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        policy.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory =
        selectedCategory === 'All Categories' || policy.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchTerm, selectedCategory]);

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Policy Explorer</h1>
          <p className="text-gray-600 max-w-2xl">
            Browse, search, and explore all compliance policies and regulatory frameworks. Click on any policy to view detailed sections, clauses, and download documents.
          </p>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-6 mb-8">
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search policies by title or keywords..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filter by Category
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {CATEGORIES.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Found <span className="font-bold text-gray-900">{filteredPolicies.length}</span> policy{' '}
              {filteredPolicies.length !== 1 ? 'policies' : ''}
            </p>
          </div>
        </div>

        {/* Policies Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPolicies.map((policy) => (
            <div
              key={policy.id}
              className="bg-white rounded-lg border-2 border-slate-200 overflow-hidden hover:shadow-lg transition"
            >
              {/* Card Header */}
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 border-b-2 border-slate-200 p-4">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="text-xs font-bold text-gray-600 uppercase tracking-wide mb-1">
                      {policy.category}
                    </p>
                    <h3 className="text-lg font-bold text-gray-900 line-clamp-2">
                      {policy.title}
                    </h3>
                  </div>
                  <div className="flex-shrink-0">
                    <Book className="w-5 h-5 text-blue-600" />
                  </div>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 space-y-4">
                {/* Version & Dates */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-xs font-semibold text-gray-600 uppercase">Version</p>
                    <p className="text-lg font-bold text-gray-900">{policy.version}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-600 uppercase">Status</p>
                    <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                      {policy.status.charAt(0).toUpperCase() + policy.status.slice(1)}
                    </span>
                  </div>
                </div>

                {/* Dates */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-600" />
                    <span className="text-gray-600">Effective: <span className="font-semibold">{policy.effectiveDate}</span></span>
                  </div>
                  <div className="text-xs text-gray-500">
                    Last updated: {policy.lastUpdated}
                  </div>
                </div>

                {/* Description */}
                <p className="text-sm text-gray-700 line-clamp-3">{policy.description}</p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-2 pt-3 border-t border-gray-200">
                  <div className="bg-blue-50 p-2 rounded-lg text-center">
                    <p className="text-xs font-semibold text-gray-600">Sections</p>
                    <p className="text-lg font-bold text-blue-600">{policy.sections}</p>
                  </div>
                  <div className="bg-purple-50 p-2 rounded-lg text-center">
                    <p className="text-xs font-semibold text-gray-600">Clauses</p>
                    <p className="text-lg font-bold text-purple-600">{policy.clauses}</p>
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="border-t-2 border-slate-200 px-4 py-3 bg-gray-50 flex gap-2">
                <button
                  onClick={() =>
                    setExpandedPolicy(expandedPolicy === policy.id ? null : policy.id)
                  }
                  className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold text-sm transition flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  {expandedPolicy === policy.id ? 'Hide Details' : 'View Details'}
                </button>
                <button className="px-3 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 font-semibold text-sm transition flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                </button>
              </div>

              {/* Expanded Details */}
              {expandedPolicy === policy.id && (
                <div className="border-t-2 border-slate-200 bg-slate-50 p-4 space-y-4">
                  <div>
                    <h4 className="font-bold text-gray-900 mb-2">Policy Overview</h4>
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {policy.description}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-bold text-gray-900">Structure</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>• <span className="font-semibold">{policy.sections} Sections</span> covering major topics</li>
                      <li>• <span className="font-semibold">{policy.clauses} Clauses</span> with specific requirements</li>
                      <li>• Latest version: <span className="font-semibold">v{policy.version}</span></li>
                      <li>• Effective since: <span className="font-semibold">{policy.effectiveDate}</span></li>
                    </ul>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div className="flex gap-2 items-start">
                      <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <p className="text-xs text-blue-900">
                        To view specific sections and clauses, use the search function or download the full PDF.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredPolicies.length === 0 && (
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No policies found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </div>
        )}

        {/* Helpful Tips */}
        <div className="mt-16 bg-white rounded-lg border-2 border-slate-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Use Policy Explorer</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mb-3">
                <Search className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Search</h3>
              <p className="text-sm text-gray-600">
                Use the search box to find policies by title, keyword, or topic.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mb-3">
                <Filter className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Filter</h3>
              <p className="text-sm text-gray-600">
                Select a category to narrow down policies by topic area.
              </p>
            </div>
            <div>
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mb-3">
                <Download className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Download</h3>
              <p className="text-sm text-gray-600">
                Download full policy documents for offline reference.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-sm text-amber-900">
            💡 <span className="font-semibold">Tip:</span> Use the{' '}
            <Link href="/query" className="text-amber-700 hover:text-amber-900 font-bold underline">
              AI Assistant
            </Link>
            {' '}to ask questions about any policy. The assistant will cite specific policies and clauses.
          </p>
        </div>
      </div>
    </div>
  );
}
