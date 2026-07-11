import React from 'react'
import { Alert } from 'react-bootstrap'

interface ErrorAlertProps {
  message: string
  onClose?: () => void
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onClose }) => (
  <Alert variant="danger" onClose={onClose} dismissible>
    <i className="bi bi-exclamation-triangle me-2"></i>
    {message}
  </Alert>
)
