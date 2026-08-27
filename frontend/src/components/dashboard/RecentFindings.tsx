import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/common/Button';
import { Finding } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';
import Link from 'next/link';

interface RecentFindingsProps {
  findings: Finding[];
  loading?: boolean;
  error?: string | null;
  maxItems?: number;
}

export function RecentFindings({
  findings,
  loading = false,
  error = null,
  maxItems = 5
}: RecentFindingsProps) {
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

  const getStatusLabel = (status: string) => {
    return status.replace('_', ' ');
  };

  if (loading) {
    return (
      <Card title="Recent Findings" subtitle="Latest security findings">
        <div className="flex items-center justify-center py-8" aria-label="Loading recent findings">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Recent Findings" subtitle="Latest security findings">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4" role="alert">
            Failed to load recent findings
          </div>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (findings.length === 0) {
    return (
      <Card title="Recent Findings" subtitle="Latest security findings">
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">No findings require attention</div>
          <p className="text-sm text-gray-400">
            This means no findings currently exist rather than a system failure
          </p>
        </div>
      </Card>
    );
  }

  const displayFindings = findings.slice(0, maxItems);

  return (
    <Card title="Recent Findings" subtitle="Latest security findings">
      <div className="space-y-3">
        {displayFindings.map((finding) => (
          <Link
            key={finding.id}
            href={`/findings/${finding.id}`}
            className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={`View finding: ${safeText(finding.title)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 mb-1">
                  {safeText(finding.title)}
                </h3>
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(finding.severity)}`}
                    aria-label={`Severity: ${safeText(finding.severity)}`}
                  >
                    {safeText(finding.severity)}
                  </span>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(finding.status)}`}
                    aria-label={`Status: ${getStatusLabel(finding.status)}`}
                  >
                    {safeText(getStatusLabel(finding.status))}
                  </span>
                  <span className="text-xs text-gray-500">
                    {safeDate(finding.created_at)}
                  </span>
                </div>
              </div>
              <div className="text-gray-400" aria-hidden="true">
                →
              </div>
            </div>
            <p className="text-sm text-gray-600">
              {truncateText(finding.description, 150)}
            </p>
          </Link>
        ))}
      </div>
      {findings.length > maxItems && (
        <div className="mt-4 text-center">
          <Link
            href="/findings"
            className="text-blue-600 hover:text-blue-800 text-sm focus:outline-none focus:underline"
          >
            View all {findings.length} findings →
          </Link>
        </div>
      )}
    </Card>
  );
}