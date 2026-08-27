import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

interface DetectionInfoProps {
  detection: any | null;
  loading?: boolean;
  error?: string | null;
}

export function DetectionInfo({ detection, loading = false, error = null }: DetectionInfoProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
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

  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
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
      <Card title="Detection Information" subtitle="Rule and detection details">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Detection Information" subtitle="Rule and detection details">
        <Alert type="error" message={error} />
      </Card>
    );
  }

  if (!detection) {
    return (
      <Card title="Detection Information" subtitle="Rule and detection details">
        <div className="text-center py-8 text-gray-500">
          No detection information available
        </div>
      </Card>
    );
  }

  return (
    <Card title="Detection Information" subtitle="Rule and detection details">
      <div className="space-y-4">
        {/* Detection Rule and Version */}
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {detection.rule_name ? safeText(detection.rule_name) : 'Unknown Rule'}
            </h3>
            {detection.rule_version && (
              <span className="text-sm text-gray-600">
                Version {safeText(detection.rule_version)}
              </span>
            )}
          </div>
          {detection.severity && (
            <span 
              className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(detection.severity)}`}
              aria-label={`Detection severity: ${safeText(detection.severity)}`}
            >
              {getSeverityIcon(detection.severity)} {safeText(detection.severity)}
            </span>
          )}
        </div>

        {/* Key Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Detection Timestamp */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Detection Timestamp</h4>
            <time className="text-sm text-gray-600" dateTime={detection.timestamp}>
              {detection.timestamp ? safeDate(detection.timestamp) : 'N/A'}
            </time>
          </div>

          {/* Severity */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Severity</h4>
            <div className="flex items-center gap-2">
              <span aria-hidden="true">{getSeverityIcon(detection.severity)}</span>
              <span className="text-sm text-gray-600">
                {detection.severity ? safeText(detection.severity) : 'N/A'}
              </span>
            </div>
          </div>

          {/* Confidence */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Confidence</h4>
            <span className="text-sm text-gray-600">
              {detection.confidence ? `${Math.round(detection.confidence * 100)}%` : 'N/A'}
            </span>
          </div>

          {/* Rule ID */}
          {detection.rule_id && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Rule ID</h4>
              <span className="text-sm text-gray-600 font-mono">
                {safeText(detection.rule_id)}
              </span>
            </div>
          )}
        </div>

        {/* Detection Metadata */}
        {detection.metadata && Object.keys(detection.metadata).length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Detection Metadata</h4>
            <div className="bg-gray-50 border border-gray-200 rounded p-3">
              <pre className="text-xs text-gray-700 overflow-x-auto">
                {JSON.stringify(detection.metadata, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Rule Description */}
        {detection.rule_description && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Rule Description</h4>
            <p className="text-sm text-gray-600">
              {truncateText(detection.rule_description, 300)}
            </p>
          </div>
        )}

        {/* Matched Conditions */}
        {detection.matched_conditions && detection.matched_conditions.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Matched Conditions</h4>
            <ul className="list-disc list-inside space-y-1">
              {detection.matched_conditions.map((condition: string, index: number) => (
                <li key={index} className="text-sm text-gray-600">
                  {safeText(condition)}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Contextual Information */}
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded">
          <p className="text-xs text-gray-700">
            <strong>Detection Context:</strong> This finding was generated by the detection rule above.
            The rule evaluated security events and identified suspicious patterns that triggered this finding.
          </p>
        </div>
      </div>
    </Card>
  );
}