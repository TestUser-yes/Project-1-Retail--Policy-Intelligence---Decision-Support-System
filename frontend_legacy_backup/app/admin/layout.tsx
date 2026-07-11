'use client';

import { useState } from 'react';
import Link from 'next/link';
import { BarChart3, Users, AlertTriangle, Settings, LogOut, Menu, X } from 'lucide-react';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gradient-to-b from-blue-900 to-blue-800 text-white p-6 transition-all duration-300`}>
        <div className="flex items-center justify-between mb-8">
          <h1 className={`text-2xl font-bold transition-all duration-300 ${sidebarOpen ? 'block' : 'hidden'}`}>Admin</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-blue-700 rounded">
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        <nav className="space-y-4">
          <Link href="/admin" className="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-700 transition">
            <BarChart3 className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Dashboard</span>}
          </Link>

          <Link href="/admin/users" className="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-700 transition">
            <Users className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Users</span>}
          </Link>

          <Link href="/admin/escalations" className="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-700 transition">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Escalations</span>}
          </Link>

          <Link href="/admin/settings" className="flex items-center gap-3 p-3 rounded-lg hover:bg-blue-700 transition">
            <Settings className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Settings</span>}
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
