import React from 'react'
import { Toast } from 'react-bootstrap'
import { Notification } from '@/hooks/useNotification'

interface ToastProps {
  notification: Notification
  onClose: () => void
}

const variantMap: Record<Notification['type'], string> = {
  success: 'success',
  error: 'danger',
  info: 'info',
  warning: 'warning',
}

export const AppToast: React.FC<ToastProps> = ({ notification, onClose }) => (
  <Toast
    onClose={onClose}
    show={true}
    delay={notification.duration}
    autohide={notification.duration !== 0}
    bg={variantMap[notification.type]}
  >
    <Toast.Body className={notification.type === 'error' ? 'text-white' : ''}>
      {notification.message}
    </Toast.Body>
  </Toast>
)
