import React from 'react'
import { ToastContainer as BSToastContainer } from 'react-bootstrap'
import { Notification } from '@/hooks/useNotification'
import { AppToast } from './Toast'

interface ToastContainerProps {
  notifications: Notification[]
  onRemove: (id: string) => void
}

export const ToastContainerComponent: React.FC<ToastContainerProps> = ({
  notifications,
  onRemove,
}) => (
  <BSToastContainer position="top-end" className="p-3" style={{ zIndex: 9999 }}>
    {notifications.map((notification) => (
      <AppToast
        key={notification.id}
        notification={notification}
        onClose={() => onRemove(notification.id)}
      />
    ))}
  </BSToastContainer>
)
