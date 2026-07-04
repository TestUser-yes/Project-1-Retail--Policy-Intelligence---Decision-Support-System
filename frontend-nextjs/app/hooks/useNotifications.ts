"use client";

import { useState, useCallback } from "react";

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback(
    (notification: Omit<Notification, "id">) => {
      const id = Date.now().toString();
      const fullNotification: Notification = {
        ...notification,
        id,
        duration: notification.duration ?? 5000,
      };

      setNotifications((prev) => [...prev, fullNotification]);

      if (fullNotification.duration) {
        setTimeout(() => removeNotification(id), fullNotification.duration);
      }

      return id;
    },
    []
  );

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const success = useCallback(
    (title: string, message: string) =>
      addNotification({ type: "success", title, message }),
    [addNotification]
  );

  const error = useCallback(
    (title: string, message: string) =>
      addNotification({ type: "error", title, message, duration: 7000 }),
    [addNotification]
  );

  const warning = useCallback(
    (title: string, message: string) =>
      addNotification({ type: "warning", title, message }),
    [addNotification]
  );

  const info = useCallback(
    (title: string, message: string) =>
      addNotification({ type: "info", title, message }),
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info,
  };
}
