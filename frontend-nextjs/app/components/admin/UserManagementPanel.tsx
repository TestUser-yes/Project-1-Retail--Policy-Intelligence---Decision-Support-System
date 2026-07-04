"use client";

import React, { useState } from "react";
import { UserPlus, Trash2, Edit2, Check, X } from "lucide-react";
import { useUserManagement, type User } from "@/app/hooks/admin/useUserManagement";

export function UserManagementPanel() {
  const {
    users,
    addUser,
    updateUserRole,
    toggleUserStatus,
    deleteUser,
    getUserStats,
  } = useUserManagement();

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ email: "", name: "", role: "viewer" as const });
  const [editingId, setEditingId] = useState<string | null>(null);

  const stats = getUserStats();

  const handleAddUser = () => {
    if (formData.email && formData.name) {
      addUser(formData.email, formData.name, formData.role as User["role"]);
      setFormData({ email: "", name: "", role: "viewer" });
      setShowForm(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Total Users</p>
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
        </div>
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Admins</p>
          <p className="text-2xl font-bold text-blue-600">{stats.admins}</p>
        </div>
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Officers</p>
          <p className="text-2xl font-bold text-purple-600">{stats.compliance_officers}</p>
        </div>
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Viewers</p>
          <p className="text-2xl font-bold text-gray-600">{stats.viewers}</p>
        </div>
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Active</p>
          <p className="text-2xl font-bold text-green-600">{stats.active}</p>
        </div>
        <div className="bg-white p-3 rounded shadow">
          <p className="text-xs text-gray-600">Inactive</p>
          <p className="text-2xl font-bold text-red-600">{stats.inactive}</p>
        </div>
      </div>

      {/* Add User Form */}
      <div className="bg-white rounded-lg shadow p-4">
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 mb-4"
        >
          <UserPlus className="w-4 h-4" />
          Add User
        </button>

        {showForm && (
          <div className="grid grid-cols-3 gap-3">
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            />
            <input
              type="text"
              placeholder="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            />
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
              className="px-3 py-2 border border-gray-300 rounded text-sm"
            >
              <option value="viewer">Viewer</option>
              <option value="compliance_officer">Compliance Officer</option>
              <option value="admin">Admin</option>
            </select>
            <button
              onClick={handleAddUser}
              className="col-span-3 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
            >
              Create User
            </button>
          </div>
        )}
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Name</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Role</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{user.name}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{user.email}</td>
                <td className="px-4 py-3 text-sm">
                  <select
                    value={user.role}
                    onChange={(e) => updateUserRole(user.id, e.target.value as User["role"])}
                    className="px-2 py-1 border border-gray-300 rounded text-xs"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="compliance_officer">Officer</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td className="px-4 py-3 text-sm">
                  <button
                    onClick={() => toggleUserStatus(user.id)}
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      user.isActive
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {user.isActive ? "Active" : "Inactive"}
                  </button>
                </td>
                <td className="px-4 py-3 text-sm space-x-2">
                  <button
                    onClick={() => toggleUserStatus(user.id)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteUser(user.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
