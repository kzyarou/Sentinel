import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/common/Button';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unavailable';
  message?: string;
  lastCheck: string;
}

interface SystemHealthProps {
  healthData: {
    api: HealthStatus;
    database: HealthStatus;
    detectionEngine: HealthStatus;
  };
  loading?: boolean;
  error?: string | null;
}

export function SystemHealth({
  healthData,
  loading = false,
  error = null
}: SystemHealthProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unavailable':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return '✓';
      case 'degraded':
        return '⚠';
      case 'unavailable':
        return '✗';
      default:
        return '?';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'Healthy';
      case 'degraded':
        return 'Degraded';
      case 'unavailable':
        return 'Unavailable';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <Card title="System Health" subtitle="Component status monitoring">
        <div className="flex items-center justify-center py-8" aria-label="Loading system health">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="System Health" subtitle="Component status monitoring">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4" role="alert">
            Failed to load system health
          </div>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  const healthComponents = [
    { key: 'api', label: 'API', data: healthData.api },
    { key: 'database', label: 'Database', data: healthData.database },
    { key: 'detectionEngine', label: 'Detection Engine', data: healthData.detectionEngine }
  ];

  return (
    <Card title="System Health" subtitle="Component status monitoring">
      <div className="space-y-4">
        {healthComponents.map((component) => (
          <div
            key={component.key}
            className="p-4 bg-gray-50 rounded-lg"
            role="status"
            aria-label={`${component.label} status: ${getStatusLabel(component.data.status)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div
                  className={`w-3 h-3 rounded-full ${
                    component.data.status === 'healthy'
                      ? 'bg-green-500'
                      : component.data.status === 'degraded'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  aria-hidden="true"
                />
                <h3 className="font-medium text-gray-900">{component.label}</h3>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(
                    component.data.status
                  )}`}
                  aria-label={`Status: ${getStatusLabel(component.data.status)}`}
                >
                  {getStatusLabel(component.data.status)}
                </span>
                <span className="text-lg" aria-hidden="true">
                  {getStatusIcon(component.data.status)}
                </span>
              </div>
            </div>
            {component.data.message && (
              <p className="text-sm text-gray-600 mb-1">
                {component.data.message}
              </p>
            )}
            <p className="text-xs text-gray-500">
              Last check: {new Date(component.data.lastCheck).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}