export default function ResultCard({ result, query }) {
  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      default:
        return 'bg-green-50 border-green-200 text-green-900';
    }
  };

  return (
    <div className="space-y-6 pb-8">
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-gray-600">Query</p>
        <p className="text-lg font-semibold text-gray-900 mt-1">{query}</p>
      </div>

      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Response</h2>
        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
          {result.result?.result || result.result}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-semibold text-gray-600 uppercase">Route</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{result.route?.toUpperCase()}</p>
        </div>

        <div className={`rounded-lg shadow p-6 border-2 ${getRiskColor(result.risk?.risk_level)}`}>
          <p className="text-sm font-semibold uppercase">Risk Level</p>
          <p className="text-3xl font-bold mt-2">{result.risk?.risk_level?.toUpperCase()}</p>
        </div>
      </div>

      {result.escalate && (
        <div className="bg-red-100 border-l-4 border-red-500 p-6 rounded-lg">
          <p className="font-bold text-red-900 text-lg">ESCALATION REQUIRED</p>
          <p className="text-red-800 mt-2">This query requires human review due to high risk or low confidence.</p>
        </div>
      )}
    </div>
  );
}
