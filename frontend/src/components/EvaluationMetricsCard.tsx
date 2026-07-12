import React from 'react'

interface EvaluationMetricsCardProps {
  title: string
  value: string | number
  status: 'good' | 'warning' | 'critical' | 'pending'
  trend?: number
  average?: string
  unit?: string
}

export const EvaluationMetricsCard: React.FC<EvaluationMetricsCardProps> = ({
  title,
  value,
  status,
  trend = 0,
  average = '',
  unit = '',
}) => {
  const statusColors = {
    good: 'success',
    warning: 'warning',
    critical: 'danger',
    pending: 'secondary',
  }

  const statusIcons = {
    good: 'bi-check-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    critical: 'bi-x-circle-fill',
    pending: 'bi-clock-fill',
  }

  const statusLabels = {
    good: 'Good',
    warning: 'Warning',
    critical: 'Critical',
    pending: 'Pending',
  }

  return (
    <div className="card h-100">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div>
            <small className="text-muted">{title}</small>
            <h5 className="mb-0 mt-2">
              {value}
              {unit && <small className="text-muted ms-1">{unit}</small>}
            </h5>
          </div>
          <div className="text-end">
            <i className={`bi ${statusIcons[status]} text-${statusColors[status]}`}></i>
            <div>
              <small className={`badge bg-${statusColors[status]}`}>
                {statusLabels[status]}
              </small>
            </div>
          </div>
        </div>

        {average && (
          <small className="text-muted d-block mt-2">Avg: {average}</small>
        )}

        {trend !== 0 && (
          <small className={`d-block mt-2 ${trend > 0 ? 'text-danger' : 'text-success'}`}>
            <i className={`bi bi-arrow-${trend > 0 ? 'up' : 'down'}`}></i>
            {Math.abs(trend)}%
          </small>
        )}
      </div>
    </div>
  )
}
