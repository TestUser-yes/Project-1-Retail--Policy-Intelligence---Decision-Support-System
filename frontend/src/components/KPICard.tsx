import React from 'react'
import { Card } from 'react-bootstrap'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: string
  variant?: 'primary' | 'success' | 'danger' | 'warning' | 'info'
  trend?: { value: number; direction: 'up' | 'down' }
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'primary',
  trend,
}) => {
  const borderColor = {
    primary: '#0d6efd',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
  }[variant]

  return (
    <Card style={{ borderLeft: `4px solid ${borderColor}` }} className="mb-3">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <Card.Title className="h6 text-muted">{title}</Card.Title>
            <div className="h4 mb-2 fw-bold">{value}</div>
            {subtitle && <Card.Text className="text-muted small">{subtitle}</Card.Text>}
          </div>
          {icon && (
            <div
              style={{
                fontSize: '24px',
                color: borderColor,
                opacity: 0.3,
              }}
            >
              <i className={`bi ${icon}`}></i>
            </div>
          )}
        </div>
        {trend && (
          <small className={trend.direction === 'up' ? 'text-success' : 'text-danger'}>
            <i
              className={`bi bi-arrow-${trend.direction} me-1`}
            ></i>
            {trend.value}%
          </small>
        )}
      </Card.Body>
    </Card>
  )
}
