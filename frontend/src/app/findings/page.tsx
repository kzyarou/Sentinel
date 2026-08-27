'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib/api';
import { Finding } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

export default function FindingsPage() {
  const router = useRouter();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getFindings();
        setFindings(response.items || []);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view findings.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch findings. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchFindings();
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

  const handleRetry = () => {
    const fetchFindings = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getFindings();
        setFindings(response.items || []);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view findings.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch findings. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchFindings();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Findings</h1>
          <p className="text-gray-600 mt-1">Security findings and investigations</p>
        </div>
        {!loading && !error && findings.length > 0 && (
          <div className="text-sm text-gray-600">
            {findings.length} finding{findings.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {loading ? (
        <Card title="Security Findings" subtitle="View and manage security findings">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
      ) : findings.length === 0 ? (
        <Card title="Security Findings" subtitle="View and manage security findings">
          <div className="text-center py-8">
            <div className="text-gray-500 mb-4">No security findings found</div>
            <Button onClick={handleRetry} variant="secondary">
              Refresh
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {findings.map((finding) => (
            <Card
              key={finding.id}
              title={safeText(finding.title)}
              subtitle={`Created: ${safeDate(finding.created_at)}`}
            >
              <div className="space-y-3">
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(finding.severity)}`}>
                    {safeText(finding.severity)}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(finding.status)}`}>
                    {safeText(finding.status.replace('_', ' '))}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">
                  {truncateText(finding.description, 200)}
                </p>
                <div className="flex gap-2">
                  <Button 
                    variant="primary" 
                    size="sm"
                    onClick={() => router.push(`/findings/${finding.id}`)}
                  >
                    View Details
                  </Button>
                  <Button variant="secondary" size="sm">
                    Request Analysis
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