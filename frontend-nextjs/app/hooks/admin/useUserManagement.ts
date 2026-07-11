"use client";

import { useState, useCallback } from "react";

export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "compliance_officer" | "viewer";
  createdAt: Date;
  lastActive?: Date;
  isActive: boolean;
}

export function useUserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      // TODO: Fetch from API
      setUsers([]);
    } catch (error) {
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addUser = useCallback((email: string, name: string, role: User["role"]) => {
    const newUser: User = {
      id: Date.now().toString(),
      email,
      name,
      role,
      createdAt: new Date(),
      isActive: true,
    };
    setUsers((prev) => [...prev, newUser]);
    return newUser;
  }, []);

  const updateUserRole = useCallback((userId: string, role: User["role"]) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, role } : u))
    );
  }, []);

  const toggleUserStatus = useCallback((userId: string) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, isActive: !u.isActive } : u))
    );
  }, []);

  const deleteUser = useCallback((userId: string) => {
    setUsers((prev) => prev.filter((u) => u.id !== userId));
  }, []);

  const getUserStats = useCallback(() => {
    return {
      total: users.length,
      admins: users.filter((u) => u.role === "admin").length,
      compliance_officers: users.filter((u) => u.role === "compliance_officer").length,
      viewers: users.filter((u) => u.role === "viewer").length,
      active: users.filter((u) => u.isActive).length,
      inactive: users.filter((u) => !u.isActive).length,
    };
  }, [users]);

  return {
    users,
    isLoading,
    fetchUsers,
    addUser,
    updateUserRole,
    toggleUserStatus,
    deleteUser,
    getUserStats,
  };
}
