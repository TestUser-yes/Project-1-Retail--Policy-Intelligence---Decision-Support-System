export default function HomePage({ setPage }) {
  return (
    <div className="bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 text-white">
      <div className="max-w-7xl mx-auto px-4 py-20 text-center min-h-[calc(100vh-200px)] flex flex-col justify-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6">Policy Intelligence System</h1>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Intelligent compliance assistance powered by multi-agent AI reasoning
        </p>
        
        <button
          onClick={() => setPage('query')}
          className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition transform hover:scale-105 inline-block mb-16"
        >
          Try Query
        </button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          <div className="bg-white bg-opacity-20 rounded-lg p-6">
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="text-xl font-bold mb-2">Multi-Agent System</h3>
            <p>Intelligent routing across RAG, SQL, and hybrid workflows</p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-6">
            <div className="text-3xl mb-2">⚠️</div>
            <h3 className="text-xl font-bold mb-2">Risk Assessment</h3>
            <p>Automatic detection of high-risk compliance scenarios</p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-6">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="text-xl font-bold mb-2">SLO Monitoring</h3>
            <p>Real-time tracking of performance metrics</p>
          </div>
        </div>
      </div>
    </div>
  );
}
