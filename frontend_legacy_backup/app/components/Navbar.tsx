'use client';

import Link from 'next/link';
import { Shield, LogOut } from 'lucide-react';
import { useState } from 'react';
import { api } from '@/app/lib/api';

export default function Navbar() {
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await api.logout();
      window.location.reload();
    } catch (err) {
      console.error('Logout failed:', err);
      alert('Logout failed. Please refresh the page.');
      setLoggingOut(false);
    }
  };

  return (
    <nav className="sticky top-0 z-50 bg-white shadow-lg border-b-2 border-blue-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
              Retail Policy AI
            </span>
          </Link>
          <div className="flex gap-2 items-center">
            <Link
              href="/dashboard"
              className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg font-semibold transition duration-200"
            >
              Dashboard
            </Link>
            <Link
              href="/query"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition duration-200 shadow-md hover:shadow-lg"
            >
              Ask Question
            </Link>
            <button
              onClick={handleLogout}
              disabled={loggingOut}
              className="px-4 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 disabled:text-gray-400 font-semibold transition duration-200 rounded-lg flex items-center gap-2"
              title="Logout and clear session"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">{loggingOut ? 'Logging out...' : 'Logout'}</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
