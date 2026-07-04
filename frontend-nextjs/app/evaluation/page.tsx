'use client';

import { useState } from 'react';
import {
  CheckSquare,
  Upload,
  Play,
  Download,
  BarChart3,
  TrendingUp,
  AlertCircle,
  Loader,
  FileText,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

interface EvaluationMetric {
  name: string;
  value: number;
  target: number;
  unit: string;
  status: 'pass' | 'warning' | 'fail';
}

interface EvaluationResult {
  timestamp: string;
  queryCount: number;
  metrics: EvaluationMetric[];
  detailedResults: Array<{
    queryId: string;
    query: string;
    expected: string;
    actual: string;
    match: boolean;
    confidence: number;
    latency: number;
  }>;
}

const SAMPLE_METRICS: EvaluationMetric[] = [
  { name: 'Task Success Rate (TSR)', value: 94, target: 90, unit: '%', status: 'pass' },
  { name: 'SQL Accuracy', value: 98, target: 95, unit: '%', status: 'pass' },
  { name: 'P95 Latency', value: 2.8, target: 3.0, unit: 's', status: 'pass' },
  { name: 'Avg Confidence', value: 92, target: 85, unit: '%', status: 'pass' },
  { name: 'Hallucination Rate', value: 0.5, target: 1.0, unit: '%', status: 'pass' },
  { name: 'Escalation Accuracy', value: 96, target: 90, unit: '%', status: 'pass' },
];

const SAMPLE_EVALUATION: EvaluationResult = {
  timestamp: '2026-01-20T14:30:00Z',
  queryCount: 50,
  metrics: SAMPLE_METRICS,
  detailedResults: [
    {
      queryId: 'Q-001',
      query: 'Can ABC Logistics be approved?',
      expected: 'No',
      actual: 'No',
      match: true,
      confidence: 94,
      latency: 2.1,
    },
    {
      queryId: 'Q-002',
      query: 'What is the data retention period?',
      expected: '7 years for transaction records',
      actual: '7 years for transaction records',
      match: true,
      confidence: 96,
      latency: 1.8,
    },
    {
      queryId: 'Q-003',
      query: 'Is cross-border transfer allowed?',
      expected: 'Requires legal review',
      actual: 'Requires legal review',
      match: true,
      confidence: 91,
      latency: 2.5,
    },
  ],
};

export default function EvaluationPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [evaluationRunning, setEvaluationRunning] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(SAMPLE_EVALUATION);
  const [activeTab, setActiveTab] = useState<'overview' | 'detailed'>('overview');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleRunEvaluation = async () => {
    setEvaluationRunning(true);
    // Simulate evaluation running
    await new Promise((resolve) => setTimeout(resolve, 3000));
    setEvaluationRunning(false);
    // In real implementation, call API with selectedFile
  };

  // Prepare radar chart data
  const radarData = SAMPLE_METRICS.map((m) => ({
    name: m.name.split('(')[0].trim(),
    value: m.value,
    target: m.target,
  }));

  // Prepare metric comparison chart
  const metricsChartData = SAMPLE_METRICS.map((m) => ({
    name: m.name.split('(')[0].trim(),
    actual: m.value,
    target: m.target,
  }));

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Evaluation Suite</h1>
          <p className="text-gray-600">
            Upload golden queries and run comprehensive SLO evaluation tests
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg border-2 border-slate-200 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Upload className="w-6 h-6" />
            Upload Golden Queries
          </h2>

          <div className="space-y-6">
            {/* File Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
              <input
                type="file"
                accept=".csv,.json"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer block">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-semibold text-gray-900 mb-2">
                  {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                </p>
                <p className="text-sm text-gray-600">CSV or JSON format (max 10MB)</p>
              </label>
            </div>

            {/* File Info */}
            {selectedFile && (
              <div className="bg-green-50 border border-green-300 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-900">
                  <CheckSquare className="w-5 h-5" />
                  <span className="font-semibold">{selectedFile.name}</span>
                  <span className="text-sm">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              </div>
            )}

            {/* Expected Format */}
            <div className="bg-blue-50 border border-blue-300 rounded-lg p-4">
              <p className="text-sm font-bold text-blue-900 mb-3">📋 Expected Format:</p>
              <pre className="text-xs text-blue-800 bg-white p-3 rounded border border-blue-200 overflow-x-auto">
{`query_id,question,expected_answer,category,risk_level,expected_route
Q-001,"Can ABC Logistics be approved?","No, due to audit findings","Vendor","HIGH","HYBRID"
Q-002,"What is data retention period?","7 years for transaction records","Policy","LOW","RAG"`}
              </pre>
            </div>

            {/* Run Evaluation Button */}
            <button
              onClick={handleRunEvaluation}
              disabled={!selectedFile || evaluationRunning}
              className={`w-full px-6 py-4 rounded-lg font-bold text-lg transition flex items-center justify-center gap-2 ${
                selectedFile && !evaluationRunning
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-600 cursor-not-allowed'
              }`}
            >
              {evaluationRunning ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Running Evaluation...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Run Evaluation Suite
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {evaluationResult && (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {evaluationResult.metrics.slice(0, 3).map((metric) => (
                <div
                  key={metric.name}
                  className="bg-white rounded-lg border-2 border-slate-200 p-6 hover:shadow-lg transition"
                >
                  <p className="text-xs font-bold text-gray-600 uppercase mb-2">
                    {metric.name}
                  </p>
                  <div className="flex items-baseline gap-2 mb-2">
                    <p className="text-3xl font-bold text-gray-900">
                      {metric.value.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-600">{metric.unit}</p>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Target: {metric.target}{metric.unit}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        metric.status === 'pass'
                          ? 'bg-green-100 text-green-800'
                          : metric.status === 'warning'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {metric.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Tab Navigation */}
            <div className="bg-white rounded-lg border-2 border-slate-200 overflow-hidden">
              <div className="flex border-b-2 border-slate-200">
                {['overview', 'detailed'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as 'overview' | 'detailed')}
                    className={`flex-1 px-6 py-4 font-bold transition ${
                      activeTab === tab
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {tab === 'overview' ? 'Overview' : 'Detailed Results'}
                  </button>
                ))}
              </div>

              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="p-8 space-y-8">
                  {/* All Metrics */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-6">All Metrics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {evaluationResult.metrics.map((metric) => (
                        <div
                          key={metric.name}
                          className="bg-slate-50 border border-slate-200 rounded-lg p-4"
                        >
                          <p className="text-xs font-bold text-gray-600 uppercase mb-2 line-clamp-1">
                            {metric.name}
                          </p>
                          <div className="flex items-baseline gap-1 mb-3">
                            <p className="text-2xl font-bold text-gray-900">
                              {metric.value.toFixed(metric.value > 10 ? 0 : 1)}
                            </p>
                            <p className="text-xs text-gray-600">{metric.unit}</p>
                          </div>
                          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                metric.status === 'pass'
                                  ? 'bg-green-500'
                                  : metric.status === 'warning'
                                  ? 'bg-yellow-500'
                                  : 'bg-red-500'
                              }`}
                              style={{
                                width: `${Math.min((metric.value / metric.target) * 100, 100)}%`,
                              }}
                            />
                          </div>
                          <p className="text-xs text-gray-600 mt-2">
                            Target: {metric.target}{metric.unit}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Radar Chart */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-6">Performance Profile</h3>
                    <ResponsiveContainer width="100%" height={400}>
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis dataKey="name" />
                        <PolarRadiusAxis domain={[0, 100]} />
                        <Radar
                          name="Actual"
                          dataKey="value"
                          stroke="#3b82f6"
                          fill="#3b82f6"
                          fillOpacity={0.5}
                        />
                        <Radar
                          name="Target"
                          dataKey="target"
                          stroke="#ef4444"
                          fill="#ef4444"
                          fillOpacity={0.1}
                        />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Metrics Comparison */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-6">Actual vs Target</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={metricsChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="actual" fill="#3b82f6" name="Actual" />
                        <Bar dataKey="target" fill="#ef4444" name="Target" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* SLO Summary */}
                  <div className="bg-green-50 border-2 border-green-300 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <CheckSquare className="w-6 h-6 text-green-600" />
                      <h4 className="text-lg font-bold text-green-900">SLO Compliance</h4>
                    </div>
                    <p className="text-green-800 mb-4">
                      ✓ All evaluation metrics meet or exceed SLO targets. System is operating within acceptable parameters.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm text-green-800">
                      <div>• Success Rate: 94% ≥ 90%</div>
                      <div>• SQL Accuracy: 98% ≥ 95%</div>
                      <div>• Latency: 2.8s ≤ 3.0s</div>
                      <div>• Confidence: 92% ≥ 85%</div>
                      <div>• Hallucination: 0.5% ≤ 1.0%</div>
                      <div>• Escalation Accuracy: 96% ≥ 90%</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Detailed Results Tab */}
              {activeTab === 'detailed' && (
                <div className="p-8">
                  <h3 className="text-lg font-bold text-gray-900 mb-6">
                    Query-by-Query Results ({evaluationResult.detailedResults.length} queries)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="border-b-2 border-slate-200 bg-slate-50">
                        <tr>
                          <th className="text-left py-3 px-4 font-bold text-gray-900">Query ID</th>
                          <th className="text-left py-3 px-4 font-bold text-gray-900">Question</th>
                          <th className="text-left py-3 px-4 font-bold text-gray-900">Match</th>
                          <th className="text-left py-3 px-4 font-bold text-gray-900">Confidence</th>
                          <th className="text-left py-3 px-4 font-bold text-gray-900">Latency</th>
                        </tr>
                      </thead>
                      <tbody>
                        {evaluationResult.detailedResults.map((result) => (
                          <tr key={result.queryId} className="border-b border-slate-200 hover:bg-slate-50">
                            <td className="py-3 px-4 font-mono text-blue-600">{result.queryId}</td>
                            <td className="py-3 px-4 text-gray-900 max-w-xs truncate">{result.query}</td>
                            <td className="py-3 px-4">
                              {result.match ? (
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                                  ✓ Match
                                </span>
                              ) : (
                                <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-bold rounded-full">
                                  ✗ Mismatch
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 font-bold">{result.confidence}%</td>
                            <td className="py-3 px-4 font-mono">{result.latency}s</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Export Buttons */}
            <div className="flex gap-4">
              <button className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-bold flex items-center justify-center gap-2 transition">
                <Download className="w-5 h-5" />
                Export as PDF
              </button>
              <button className="flex-1 px-6 py-3 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 font-bold flex items-center justify-center gap-2 transition">
                <Download className="w-5 h-5" />
                Export as CSV
              </button>
            </div>
          </div>
        )}

        {/* Help Section */}
        <div className="mt-12 bg-amber-50 border-2 border-amber-300 rounded-lg p-8">
          <h3 className="text-lg font-bold text-amber-900 mb-4">📚 How to Use Evaluation Suite</h3>
          <ul className="space-y-2 text-sm text-amber-800">
            <li>• <span className="font-bold">Prepare Golden Queries:</span> Create a CSV/JSON file with expected answers</li>
            <li>• <span className="font-bold">Upload File:</span> Use the upload area above to submit your golden queries</li>
            <li>• <span className="font-bold">Run Evaluation:</span> Click "Run Evaluation Suite" to test all queries</li>
            <li>• <span className="font-bold">Review Results:</span> Check metrics against SLO targets</li>
            <li>• <span className="font-bold">Export Report:</span> Download results for documentation</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
