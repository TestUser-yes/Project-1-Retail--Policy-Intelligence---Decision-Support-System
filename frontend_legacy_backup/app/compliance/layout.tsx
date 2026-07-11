'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Briefcase, CheckSquare, Clock, BarChart3, LogOut, Menu, X } from 'lucide-react';

export default function ComplianceLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gradient-to-b from-amber-900 to-amber-800 text-white p-6 transition-all duration-300`}>
        <div className="flex items-center justify-between mb-8">
          <h1 className={`text-xl font-bold transition-all duration-300 ${sidebarOpen ? 'block' : 'hidden'}`}>Compliance</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-amber-700 rounded">
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        <nav className="space-y-4">
          <Link href="/compliance" className="flex items-center gap-3 p-3 rounded-lg hover:bg-amber-700 transition">
            <BarChart3 className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Dashboard</span>}
          </Link>

          <Link href="/compliance/handoffs" className="flex items-center gap-3 p-3 rounded-lg hover:bg-amber-700 transition">
            <Briefcase className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Handoffs</span>}
          </Link>

          <Link href="/compliance/sla-monitoring" className="flex items-center gap-3 p-3 rounded-lg hover:bg-amber-700 transition">
            <Clock className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>SLA Monitoring</span>}
          </Link>

          <Link href="/compliance/resolutions" className="flex items-center gap-3 p-3 rounded-lg hover:bg-amber-700 transition">
            <CheckSquare className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Resolutions</span>}
          </Link>

          <button className="flex items-center gap-3 p-3 rounded-lg hover:bg-red-700 transition w-full">
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 p-8">
        {children}
      </div>
    </div>
  );
}
