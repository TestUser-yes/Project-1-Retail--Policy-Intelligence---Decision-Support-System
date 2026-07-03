'use client';

import { useState, useEffect } from 'react';
import { Trash2, Edit, Plus, Search, ChevronUp, ChevronDown } from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setUsers([
      { id: 1, name: 'John Doe', email: 'john@example.com', role: 'user', status: 'active', joinedAt: '2026-06-01' },
      { id: 2, name: 'Sarah Smith', email: 'sarah@example.com', role: 'compliance_officer', status: 'active', joinedAt: '2026-05-15' },
      { id: 3, name: 'Admin User', email: 'admin@example.com', role: 'admin', status: 'active', joinedAt: '2026-01-10' },
      { id: 4, name: 'Mike Johnson', email: 'mike@example.com', role: 'user', status: 'inactive', joinedAt: '2026-03-20' },
      { id: 5, name: 'Emily Chen', email: 'emily@example.com', role: 'user', status: 'active', joinedAt: '2026-06-15' },
    ]);
  };

  const filteredUsers = users
    .filter(user => user.name.toLowerCase().includes(searchTerm.toLowerCase()) || user.email.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const SortHeader = ({ field, label }: any) => (
    <button onClick={() => handleSort(field)} className="flex items-center gap-2 hover:text-blue-600 transition">
      <span>{label}</span>
      {sortBy === field && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
    </button>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          <Plus className="w-5 h-5" />
          Add User
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search users by name or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                <SortHeader field="name" label="Name" />
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                <SortHeader field="email" label="Email" />
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                <SortHeader field="role" label="Role" />
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                <SortHeader field="status" label="Status" />
              </th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Joined</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredUsers.map(user => (
              <tr key={user.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{user.name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                <td className="px-6 py-4 text-sm">
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-semibold">
                    {user.role}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    user.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{user.joinedAt}</td>
                <td className="px-6 py-4 text-sm">
                  <div className="flex gap-3">
                    <button className="text-blue-600 hover:text-blue-900 transition p-1 hover:bg-blue-50 rounded">
                      <Edit className="w-5 h-5" />
                    </button>
                    <button className="text-red-600 hover:text-red-900 transition p-1 hover:bg-red-50 rounded">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center pt-4">
        <p className="text-sm text-gray-600">Showing {filteredUsers.length} of {users.length} users</p>
        <div className="flex gap-2">
          <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50">Previous</button>
          <button className="px-3 py-1 bg-blue-600 text-white rounded">1</button>
          <button className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50">Next</button>
        </div>
      </div>
    </div>
  );
}
