import React from 'react'
import { Spinner } from 'react-bootstrap'

interface LoadingSpinnerProps {
  message?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Loading...' }) => (
  <div className="loading">
    <div className="text-center">
      <Spinner animation="border" role="status" className="mb-3">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
      <p className="text-muted">{message}</p>
    </div>
  </div>
)
