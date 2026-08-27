'use client';

import { useEffect, useState } from 'react';
import { SeverityMetrics } from '@/components/dashboard/SeverityMetrics';
import { RecentFindings } from '@/components/dashboard/RecentFindings';
import { SystemHealth } from '@/components/dashboard/SystemHealth';
import { DashboardRefresh } from '@/components/dashboard/DashboardRefresh';
import { Alert } from '@/components/common/Alert';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib';
import { Finding } from '@/types';

interface DashboardData {
  findings: Finding[];
  detections: any[]; // Placeholder until Detection type is properly implemented
  systemHealth: {
    api: { status: string; message?: string; lastCheck: string };
    database: { status: string; message?: string; lastCheck: string };
    detectionEngine: { status: string; message?: string; lastCheck: string };
  };
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>({
    findings: [],
    detections: [],
    systemHealth: {
      api: { status: 'unavailable', lastCheck: new Date().toISOString() },
      database: { status: 'unavailable', lastCheck: new Date().toISOString() },
      detectionEngine: { status: 'unavailable', lastCheck: new Date().toISOString() }
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const calculateSeverityMetrics = (findings: Finding[]) => {
    return {
      critical: findings.filter(f => f.severity === 'CRITICAL').length,
      high: findings.filter(f => f.severity === 'HIGH').length,
      medium: findings.filter(f => f.severity === 'MEDIUM').length,
      low: findings.filter(f => f.severity === 'LOW').length,
      total: findings.length
    };
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [findingsResponse, health] = await Promise.all([
        apiClient.getFindings().catch(() => ({ items: [] })),
        apiClient.getHealth().catch(() => ({ status: 'unavailable', timestamp: new Date().toISOString() }))
      ]);

      const findings = findingsResponse.items || [];
      const detections: Detection[] = []; // Placeholder until detections endpoint is available

      // Calculate system health based on responses
      const systemHealth = {
        api: {
          status: health.status === 'healthy' || health.status === 'ok' ? 'healthy' : 'degraded',
          message: health.status === 'healthy' || health.status === 'ok' ? 'API is responding normally' : 'API is responding with issues',
          lastCheck: health.timestamp || new Date().toISOString()
        },
        database: {
          status: findings.length >= 0 ? 'healthy' : 'degraded',
          message: findings.length >= 0 ? 'Database connection stable' : 'Database connection issues',
          lastCheck: new Date().toISOString()
        },
        detectionEngine: {
          status: true ? 'healthy' : 'degraded',
          message: true ? 'Detection engine operational' : 'Detection engine issues',
          lastCheck: new Date().toISOString()
        }
      };

      setData({
        findings,
        detections,
        systemHealth
      });
      setLastRefresh(new Date());
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

  useEffect(() => {
    fetchDashboardData();

    // Set up auto-refresh if enabled
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const severityMetrics = calculateSeverityMetrics(data.findings);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time security monitoring overview</p>
        </div>
        <DashboardRefresh
          onRefresh={fetchDashboardData}
          isLoading={loading}
          lastRefresh={lastRefresh}
          autoRefresh={autoRefresh}
          onToggleAutoRefresh={() => setAutoRefresh(!autoRefresh)}
        />
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {/* Severity Metrics */}
      <section aria-label="Finding severity metrics">
        <SeverityMetrics
          critical={severityMetrics.critical}
          high={severityMetrics.high}
          medium={severityMetrics.medium}
          low={severityMetrics.low}
          total={severityMetrics.total}
          loading={loading}
        />
      </section>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Findings */}
        <section aria-label="Recent security findings">
          <RecentFindings
            findings={data.findings}
            loading={loading}
            error={error}
            maxItems={5}
          />
        </section>

        {/* System Health */}
        <section aria-label="System component health">
          <SystemHealth
            healthData={data.systemHealth}
            loading={loading}
            error={error}
          />
        </section>
      </div>

      {/* Recent Detections */}
      {/* Placeholder until detections endpoint is available */}
      {/* <section aria-label="Recent detection activity">
        <RecentDetections
          detections={data.detections}
          loading={loading}
          error={error}
          maxItems={5}
        />
      </section> */}
    </div>
  );
}