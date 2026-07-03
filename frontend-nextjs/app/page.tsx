import Link from "next/link";
import { Shield, AlertTriangle, Zap } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Shield className="w-16 h-16 text-blue-600" />
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Retail Policy Intelligence
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI-powered compliance system with smart escalation and SLO monitoring
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/query"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition transform hover:scale-105"
            >
              Ask a Question
            </Link>
            <a
              href="http://localhost:8000/docs"
              className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 font-semibold transition"
            >
              API Documentation
            </a>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition transform hover:scale-105">
            <div className="flex items-center mb-4">
              <AlertTriangle className="w-8 h-8 text-red-500 mr-3" />
              <h3 className="text-xl font-bold text-gray-800">Out-of-Scope Detection</h3>
            </div>
            <p className="text-gray-600">
              Automatically detects queries outside retail policy scope and routes them to compliance officers for proper handling.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition transform hover:scale-105">
            <div className="flex items-center mb-4">
              <Zap className="w-8 h-8 text-yellow-500 mr-3" />
              <h3 className="text-xl font-bold text-gray-800">SLO Metrics</h3>
            </div>
            <p className="text-gray-600">
              Real-time Service Level Objective tracking with color-coded status indicators for latency and compliance monitoring.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition transform hover:scale-105">
            <div className="flex items-center mb-4">
              <Shield className="w-8 h-8 text-green-500 mr-3" />
              <h3 className="text-xl font-bold text-gray-800">Escalation & Handoff</h3>
            </div>
            <p className="text-gray-600">
              Seamless handoff workflow for complex queries with audit trails and compliance officer assignment.
            </p>
          </div>
        </div>

        <div className="mt-20 bg-blue-50 rounded-lg p-12 text-center border-2 border-blue-200">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Backend Status</h2>
          <div className="flex justify-center items-center gap-2 mb-4">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <p className="text-lg text-green-600 font-semibold">Backend Connected & Ready ✓</p>
          </div>
          <p className="text-gray-600">
            System is fully operational and ready to handle policy queries with intelligent escalation.
          </p>
        </div>

        <div className="mt-12 grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Example: In-Scope Query</h3>
            <code className="text-sm bg-gray-100 p-3 rounded block text-gray-700">
              "What is our refund policy?"
            </code>
            <p className="text-sm text-gray-600 mt-2">✓ Answered with SLO metrics and no escalation</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Example: Out-of-Scope Query</h3>
            <code className="text-sm bg-gray-100 p-3 rounded block text-gray-700">
              "Tell me a joke"
            </code>
            <p className="text-sm text-gray-600 mt-2">✓ Automatically escalated to compliance officer</p>
          </div>
        </div>
      </div>
    </main>
  );
}
