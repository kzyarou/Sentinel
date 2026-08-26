'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib';
import { Finding, Event, DetectionRule } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

interface DashboardStats {
  totalFindings: number;
  criticalFindings: number;
  eventsToday: number;
  activeRules: number;
  systemHealthy: boolean;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalFindings: 0,
    criticalFindings: 0,
    eventsToday: 0,
    activeRules: 0,
    systemHealthy: false,
  });
  const [recentEvents, setRecentEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [findingsResponse, eventsResponse, rulesResponse, health] = await Promise.all([
          apiClient.getFindings(),
          apiClient.getEvents(),
          apiClient.getDetectionRules(),
          apiClient.getHealth().catch(() => ({ status: 'unknown', timestamp: new Date().toISOString() })),
        ]);

        const findings = findingsResponse.items || [];
        const events = eventsResponse.items || [];
        const rules = rulesResponse || [];

        // Calculate statistics
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const eventsToday = events.filter(
          (event) => new Date(event.timestamp) >= today
        ).length;

        const criticalFindings = findings.filter(
          (finding) => finding.severity.toLowerCase() === 'critical'
        ).length;

        const activeRules = rules.filter((rule) => rule.enabled).length;

        setStats({
          totalFindings: findings.length,
          criticalFindings,
          eventsToday,
          activeRules,
          systemHealthy: health.status.toLowerCase() === 'healthy' || health.status.toLowerCase() === 'ok',
        });

        // Get recent events (last 5)
        setRecentEvents(events.slice(0, 5));
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view the dashboard.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch dashboard data. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleRetry = () => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [findingsResponse, eventsResponse, rulesResponse, health] = await Promise.all([
          apiClient.getFindings(),
          apiClient.getEvents(),
          apiClient.getDetectionRules(),
          apiClient.getHealth().catch(() => ({ status: 'unknown', timestamp: new Date().toISOString() })),
        ]);

        const findings = findingsResponse.items || [];
        const events = eventsResponse.items || [];
        const rules = rulesResponse || [];

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const eventsToday = events.filter(
          (event) => new Date(event.timestamp) >= today
        ).length;

        const criticalFindings = findings.filter(
          (finding) => finding.severity.toLowerCase() === 'critical'
        ).length;

        const activeRules = rules.filter((rule) => rule.enabled).length;

        setStats({
          totalFindings: findings.length,
          criticalFindings,
          eventsToday,
          activeRules,
          systemHealthy: health.status.toLowerCase() === 'healthy' || health.status.toLowerCase() === 'ok',
        });

        setRecentEvents(events.slice(0, 5));
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view the dashboard.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch dashboard data. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType.toLowerCase()) {
      case 'security':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'system':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'network':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'application':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Security monitoring overview</p>
        </div>
        {!loading && !error && (
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${stats.systemHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-600">
              {stats.systemHealthy ? 'System Healthy' : 'System Unhealthy'}
            </span>
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} title="Loading..." subtitle="Fetching data">
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner />
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <>
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card title="Total Findings" subtitle="Security findings">
              <div className="text-4xl font-bold text-blue-600">{stats.totalFindings}</div>
            </Card>
            <Card title="Critical" subtitle="High severity findings">
              <div className="text-4xl font-bold text-red-600">{stats.criticalFindings}</div>
            </Card>
            <Card title="Events Today" subtitle="Security events">
              <div className="text-4xl font-bold text-green-600">{stats.eventsToday}</div>
            </Card>
            <Card title="Active Rules" subtitle="Detection rules">
              <div className="text-4xl font-bold text-purple-600">{stats.activeRules}</div>
            </Card>
          </div>

          <Card title="Recent Activity" subtitle="Latest security events">
            {recentEvents.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-500 mb-4">No recent activity</div>
                <Button onClick={handleRetry} variant="secondary">
                  Refresh
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {recentEvents.map((event) => (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getEventTypeColor(event.event_type)}`}>
                          {safeText(event.event_type)}
                        </span>
                        <span className="text-sm text-gray-600">{safeDate(event.timestamp)}</span>
                      </div>
                      <p className="text-sm text-gray-700">{truncateText(event.message, 100)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}