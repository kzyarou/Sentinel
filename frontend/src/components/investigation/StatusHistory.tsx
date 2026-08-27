import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { safeText, safeDate } from '@/lib/safe-rendering';

interface StatusHistoryEntry {
  id: string;
  status: string;
  previous_status?: string;
  timestamp: string;
  actor?: string;
  reason?: string;
}

interface StatusHistoryProps {
  statusHistory: StatusHistoryEntry[];
  loading?: boolean;
  error?: string | null;
}

const STATUS_LABELS: Record<string, string> = {
  'OPEN': 'Open',
  'INVESTIGATING': 'Investigating',
  'RESOLVED': 'Resolved',
  'FALSE_POSITIVE': 'False Positive'
};

const STATUS_COLORS: Record<string, string> = {
  'OPEN': 'bg-red-100 text-red-800',
  'INVESTIGATING': 'bg-yellow-100 text-yellow-800',
  'RESOLVED': 'bg-green-100 text-green-800',
  'FALSE_POSITIVE': 'bg-gray-100 text-gray-800'
};

export function StatusHistory({ statusHistory, loading = false, error = null }: StatusHistoryProps) {
  if (loading) {
    return (
      <Card title="Status History" subtitle="Finding status changes over time">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Status History" subtitle="Finding status changes over time">
        <Alert type="error" message={error} />
      </Card>
    );
  }

  if (!statusHistory || statusHistory.length === 0) {
    return (
      <Card title="Status History" subtitle="Finding status changes over time">
        <div className="text-center py-8 text-gray-500">
          <p className="mb-4">No status history available.</p>
          <p className="text-sm text-gray-400">
            Status changes will be recorded here as the finding is investigated.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Status History" subtitle="Finding status changes over time">
      <div className="space-y-4">
        {/* Privacy Notice */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-800">
            <strong>Privacy:</strong> Status history is displayed without exposing personal or sensitive information.
            Actor information is anonymized where appropriate.
          </p>
        </div>

        {/* Timeline */}
        <div className="space-y-3">
          {statusHistory.map((entry, index) => (
            <div key={entry.id} className="flex gap-3">
              {/* Timeline Line */}
              <div className="flex flex-col items-center">
                {index < statusHistory.length - 1 && (
                  <div className="w-0.5 h-full bg-gray-300" />
                )}
                <div className="w-3 h-3 rounded-full bg-blue-500 border-2 border-white shadow" />
              </div>

              {/* Entry Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {entry.previous_status && (
                      <>
                        <span 
                          className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[entry.previous_status]}`}
                          aria-label={`Previous status: ${STATUS_LABELS[entry.previous_status]}`}
                        >
                          {STATUS_LABELS[entry.previous_status]}
                        </span>
                        <span className="text-gray-400" aria-hidden="true">→</span>
                      </>
                    )}
                    <span 
                      className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[entry.status]}`}
                      aria-label={`New status: ${STATUS_LABELS[entry.status]}`}
                    >
                      {STATUS_LABELS[entry.status]}
                    </span>
                  </div>
                  <time className="text-xs text-gray-500" dateTime={entry.timestamp}>
                    {safeDate(entry.timestamp)}
                  </time>
                </div>

                {/* Change Reason */}
                {entry.reason && (
                  <p className="text-sm text-gray-600 mb-1">
                    {safeText(entry.reason)}
                  </p>
                )}

                {/* Actor Information */}
                {entry.actor && (
                  <p className="text-xs text-gray-500">
                    Changed by: {safeText(entry.actor)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Audit Information */}
        <div className="p-3 bg-gray-50 border border-gray-200 rounded">
          <p className="text-xs text-gray-700">
            <strong>Audit Information:</strong> All status changes are logged in the security audit system.
            These changes correspond to backend audit events for accountability and compliance.
          </p>
        </div>
      </div>
    </Card>
  );
}