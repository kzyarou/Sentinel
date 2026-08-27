'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib/api';
import { DetectionRule } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

export default function DetectionsPage() {
  const [rules, setRules] = useState<DetectionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getDetectionRules();
        setRules(data);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view detection rules.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch detection rules. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, []);

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
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const handleSeedRules = async () => {
    try {
      setSeeding(true);
      setError(null);
      await apiClient.seedDetectionRules();
      const data = await apiClient.getDetectionRules();
      setRules(data);
    } catch (err) {
      if (err instanceof NetworkError) {
        setError('Unable to connect to the backend server. Please check if the backend is running.');
      } else if (err instanceof AuthenticationError) {
        setError('Authentication required. Please log in to manage detection rules.');
      } else if (err instanceof ServerError) {
        setError('Backend server error. Please try again later.');
      } else {
        setError('Failed to seed detection rules. Please try again.');
      }
    } finally {
      setSeeding(false);
    }
  };

  const handleRetry = () => {
    const fetchRules = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.getDetectionRules();
        setRules(data);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view detection rules.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch detection rules. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Detection Rules</h1>
          <p className="text-gray-600 mt-1">Manage detection rules and patterns</p>
        </div>
        {!loading && !error && (
          <div className="flex gap-2">
            <Button onClick={handleSeedRules} variant="secondary" disabled={seeding}>
              {seeding ? 'Seeding...' : 'Seed Rules'}
            </Button>
            <Button onClick={handleRetry} variant="secondary">
              Refresh
            </Button>
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {loading ? (
        <Card title="Detection Rules" subtitle="Configure detection patterns">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
      ) : rules.length === 0 ? (
        <Card title="Detection Rules" subtitle="Configure detection patterns">
          <div className="text-center py-8">
            <div className="text-gray-500 mb-4">No detection rules found</div>
            <Button onClick={handleSeedRules} variant="primary" disabled={seeding}>
              {seeding ? 'Seeding...' : 'Seed Initial Rules'}
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {rules.map((rule) => (
            <Card
              key={rule.id}
              title={safeText(rule.name)}
              subtitle={`Updated: ${safeDate(rule.updated_at)}`}
            >
              <div className="space-y-3">
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(rule.severity)}`}>
                    {safeText(rule.severity)}
                  </span>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {safeText(rule.rule_type)}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${rule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {rule.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">
                  {truncateText(rule.description, 200)}
                </p>
                <div className="flex gap-2">
                  <Button variant="primary" size="sm">
                    View Details
                  </Button>
                  <Button variant="secondary" size="sm">
                    Edit
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}