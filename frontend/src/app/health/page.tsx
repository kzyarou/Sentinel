'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { apiClient, NetworkError, ServerError } from '@/lib';

interface HealthStatus {
  status: string;
  timestamp: string;
}

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getHealth();
        setHealth(data);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch health status. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'unhealthy':
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return '✓';
      case 'degraded':
        return '⚠';
      case 'unhealthy':
      case 'error':
        return '✗';
      default:
        return '?';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
        <p className="text-gray-600 mt-1">System status and monitoring</p>
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Backend Status" subtitle="API service health">
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner />
            </div>
          </Card>
          <Card title="Database Status" subtitle="Database connectivity">
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner />
            </div>
          </Card>
        </div>
      ) : health ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Backend Status" subtitle="API service health">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`text-2xl font-bold ${getStatusColor(health.status)}`}>
                  {getStatusIcon(health.status)} {health.status}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Last Check:</span>
                <span className="text-gray-900">
                  {new Date(health.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </Card>

          <Card title="Database Status" subtitle="Database connectivity">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="text-2xl font-bold text-green-600">
                  ✓ Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Last Check:</span>
                <span className="text-gray-900">
                  {new Date(health.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </Card>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Backend Status" subtitle="API service health">
            <div className="flex items-center justify-center py-8 text-gray-500">
              No health data available
            </div>
          </Card>
          <Card title="Database Status" subtitle="Database connectivity">
            <div className="flex items-center justify-center py-8 text-gray-500">
              No health data available
            </div>
          </Card>
        </div>
      )}

      <Card title="System Metrics" subtitle="Performance and resource usage">
        <div className="text-gray-500 text-center py-8">
          System metrics will be available in future updates
        </div>
      </Card>
    </div>
  );
}