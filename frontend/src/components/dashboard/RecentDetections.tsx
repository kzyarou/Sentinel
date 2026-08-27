import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/common/Button';
import { Detection } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

interface RecentDetectionsProps {
  detections: Detection[];
  loading?: boolean;
  error?: string | null;
  maxItems?: number;
}

export function RecentDetections({
  detections,
  loading = false,
  error = null,
  maxItems = 5
}: RecentDetectionsProps) {
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

  if (loading) {
    return (
      <Card title="Recent Detections" subtitle="Latest detection activity">
        <div className="flex items-center justify-center py-8" aria-label="Loading recent detections">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Recent Detections" subtitle="Latest detection activity">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4" role="alert">
            Failed to load recent detections
          </div>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (detections.length === 0) {
    return (
      <Card title="Recent Detections" subtitle="Latest detection activity">
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">No recent detection activity</div>
          <p className="text-sm text-gray-400">
            Detection pipeline may be inactive or no rules have triggered
          </p>
        </div>
      </Card>
    );
  }

  const displayDetections = detections.slice(0, maxItems);

  return (
    <Card title="Recent Detections" subtitle="Latest detection activity">
      <div className="space-y-3">
        {displayDetections.map((detection) => (
          <div
            key={detection.id}
            className="p-4 bg-gray-50 rounded-lg"
            role="article"
            aria-label={`Detection: ${safeText(detection.rule_name)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 mb-1">
                  {safeText(detection.rule_name)}
                </h3>
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(detection.severity)}`}
                    aria-label={`Severity: ${safeText(detection.severity)}`}
                  >
                    {safeText(detection.severity)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {safeDate(detection.matched_at)}
                  </span>
                </div>
              </div>
            </div>
            {detection.details && (
              <p className="text-sm text-gray-600">
                {truncateText(JSON.stringify(detection.details), 150)}
              </p>
            )}
            {detection.finding_id && (
              <div className="mt-2 text-xs text-gray-500">
                Related finding: {safeText(detection.finding_id)}
              </div>
            )}
          </div>
        ))}
      </div>
      {detections.length > maxItems && (
        <div className="mt-4 text-center">
          <a
            href="/detections"
            className="text-blue-600 hover:text-blue-800 text-sm focus:outline-none focus:underline"
          >
            View all {detections.length} detections →
          </a>
        </div>
      )}
    </Card>
  );
}