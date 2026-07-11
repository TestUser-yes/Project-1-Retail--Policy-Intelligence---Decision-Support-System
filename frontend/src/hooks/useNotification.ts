import { useState, useCallback } from 'react'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

export const useNotification = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = useCallback((
    message: string,
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    duration = 5000
  ) => {
    const id = Date.now().toString()
    const notification: Notification = { id, message, type, duration }

    setNotifications((prev) => [...prev, notification])

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const success = useCallback((message: string) => {
    return addNotification(message, 'success')
  }, [addNotification])

  const error = useCallback((message: string) => {
    return addNotification(message, 'error')
  }, [addNotification])

  const info = useCallback((message: string) => {
    return addNotification(message, 'info')
  }, [addNotification])

  const warning = useCallback((message: string) => {
    return addNotification(message, 'warning')
  }, [addNotification])

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    info,
    warning,
  }
}
