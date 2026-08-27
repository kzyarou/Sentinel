import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Finding } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

interface FindingSummaryProps {
  finding: Finding | null;
  loading?: boolean;
  error?: string | null;
}

export function FindingSummary({ finding, loading = false, error = null }: FindingSummaryProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'info':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'resolved':
        return 'bg-green-100 text-green-800';
      case 'false_positive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      case 'low':
        return '🔵';
      case 'info':
        return '⚪';
      default:
        return '⚪';
    }
  };

  if (loading) {
    return (
      <Card title="Finding Summary" subtitle="Overview of the security finding">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Finding Summary" subtitle="Overview of the security finding">
        <Alert type="error" message={error} />
      </Card>
    );
  }

  if (!finding) {
    return (
      <Card title="Finding Summary" subtitle="Overview of the security finding">
        <div className="text-center py-8 text-gray-500">
          No finding data available
        </div>
      </Card>
    );
  }

  return (
    <Card title="Finding Summary" subtitle="Overview of the security finding">
      <div className="space-y-4">
        {/* Title and Status */}
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {safeText(finding.title)}
            </h3>
            <div className="flex gap-2 flex-wrap">
              <span 
                className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(finding.severity)}`}
                aria-label={`Severity: ${safeText(finding.severity)}`}
              >
                {getSeverityIcon(finding.severity)} {safeText(finding.severity)}
              </span>
              <span 
                className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(finding.status)}`}
                aria-label={`Status: ${safeText(finding.status.replace('_', ' '))}`}
              >
                {safeText(finding.status.replace('_', ' '))}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Description</h4>
          <p className="text-gray-600 text-sm">
            {truncateText(finding.description, 500)}
          </p>
        </div>

        {/* Key Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Severity */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Severity</h4>
            <div className="flex items-center gap-2">
              <span aria-hidden="true">{getSeverityIcon(finding.severity)}</span>
              <span className="text-sm text-gray-600">{safeText(finding.severity)}</span>
            </div>
          </div>

          {/* Confidence */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Confidence</h4>
            <span className="text-sm text-gray-600">
              {finding.confidence ? `${Math.round(finding.confidence * 100)}%` : 'N/A'}
            </span>
          </div>

          {/* Status */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Status</h4>
            <span className="text-sm text-gray-600">
              {safeText(finding.status.replace('_', ' '))}
            </span>
          </div>

          {/* Detection Category */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Detection Category</h4>
            <span className="text-sm text-gray-600">
              {finding.category ? safeText(finding.category) : 'N/A'}
            </span>
          </div>

          {/* Created Timestamp */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Created</h4>
            <time className="text-sm text-gray-600" dateTime={finding.created_at}>
              {safeDate(finding.created_at)}
            </time>
          </div>

          {/* Updated Timestamp */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Last Updated</h4>
            <time className="text-sm text-gray-600" dateTime={finding.updated_at}>
              {safeDate(finding.updated_at)}
            </time>
          </div>
        </div>

        {/* Authoritative vs AI Content Label */}
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-800">
            <strong>Note:</strong> This section displays authoritative finding information from the detection system.
            AI-assisted analysis is displayed separately below.
          </p>
        </div>
      </div>
    </Card>
  );
}