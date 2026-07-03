'use client';

import Link from 'next/link';
import { Shield } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md border-b-2 border-blue-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center gap-2">
            <Shield className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
              Policy Intelligence
            </span>
          </Link>
          <div className="flex gap-4">
            <Link
              href="/"
              className="px-4 py-2 text-gray-700 hover:text-blue-600 font-semibold transition"
            >
              Home
            </Link>
            <Link
              href="/query"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition"
            >
              Ask Question
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
