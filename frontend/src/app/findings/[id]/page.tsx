'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError, AuthorizationError, NotFoundError } from '@/lib/api';
import { Finding, AIAnalysis, Event } from '@/types';
import { FindingSummary } from '@/components/investigation/FindingSummary';
import { DetectionInfo } from '@/components/investigation/DetectionInfo';
import { Evidence } from '@/components/investigation/Evidence';
import { AIAnalysis as AIAnalysisComponent } from '@/components/investigation/AIAnalysis';
import { FindingStatus } from '@/components/investigation/FindingStatus';
import { StatusHistory } from '@/components/investigation/StatusHistory';

interface InvestigationData {
  finding: Finding | null;
  detection: any | null;
  evidence: Event[];
  aiAnalysis: AIAnalysis | null;
  statusHistory: any[];
}

export default function FindingInvestigationPage() {
  const params = useParams();
  const router = useRouter();
  const findingId = params.id as string;
  
  const [data, setData] = useState<InvestigationData>({
    finding: null,
    detection: null,
    evidence: [],
    aiAnalysis: null,
    statusHistory: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const fetchInvestigationData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch finding details
      const finding = await apiClient.getFinding(findingId);
      
      // Fetch evidence (events related to this finding)
      // This assumes events have a finding_id field or similar relationship
      const eventsResponse = await apiClient.getEvents();
      const evidence = eventsResponse.items?.filter(
        (event: Event) => event.finding_id === findingId
      ) || [];

      // Fetch AI analysis if available
      let aiAnalysis = null;
      if (finding.ai_analysis_id) {
        try {
          aiAnalysis = await apiClient.getAIAnalysis(finding.ai_analysis_id);
        } catch (err) {
          // AI analysis might not exist or be accessible
          console.warn('Could not fetch AI analysis:', err);
        }
      }

      // Fetch detection information
      let detection = null;
      if (finding.detection_id) {
        try {
          detection = await apiClient.getDetection(finding.detection_id);
        } catch (err) {
          console.warn('Could not fetch detection:', err);
        }
      }

      setData({
        finding,
        detection,
        evidence,
        aiAnalysis,
        statusHistory: [] // TODO: Fetch from audit logs when available
      });
    } catch (err) {
      if (err instanceof NotFoundError) {
        setError('Finding not found. It may have been deleted or you may not have access.');
      } else if (err instanceof AuthorizationError) {
        setError('You do not have permission to view this finding.');
      } else if (err instanceof AuthenticationError) {
        setError('Authentication required. Please log in to view this finding.');
      } else if (err instanceof NetworkError) {
        setError('Unable to connect to the backend server. Please check if the backend is running.');
      } else if (err instanceof ServerError) {
        setError('Backend server error. Please try again later.');
      } else {
        setError('Failed to fetch finding details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAnalysis = async () => {
    if (!data.finding) return;

    try {
      setAnalysisLoading(true);
      setAnalysisError(null);
      
      const updatedFinding = await apiClient.requestFindingAnalysis(data.finding.id);
      
      // Fetch the AI analysis after request completes
      if (updatedFinding.ai_analysis_id) {
        const aiAnalysis = await apiClient.getAIAnalysis(updatedFinding.ai_analysis_id);
        setData(prev => ({ ...prev, finding: updatedFinding, aiAnalysis }));
      } else {
        setData(prev => ({ ...prev, finding: updatedFinding }));
      }
    } catch (err) {
      if (err instanceof AuthorizationError) {
        setAnalysisError('You do not have permission to request AI analysis.');
      } else if (err instanceof ServerError) {
        setAnalysisError('AI analysis service is currently unavailable.');
      } else {
        setAnalysisError('Failed to request AI analysis. Please try again.');
      }
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!data.finding) return;

    try {
      const updatedFinding = await apiClient.updateFinding(data.finding.id, { status: newStatus });
      setData(prev => ({ ...prev, finding: updatedFinding }));
    } catch (err) {
      if (err instanceof AuthorizationError) {
        setError('You do not have permission to update the finding status.');
      } else if (err instanceof ServerError) {
        setError('Failed to update finding status. Please try again.');
      } else {
        setError('Failed to update finding status. Please try again.');
      }
    }
  };

  useEffect(() => {
    if (findingId) {
      fetchInvestigationData();
    }
  }, [findingId]);

  const handleBack = () => {
    router.push('/findings');
  };

  const handleRetry = () => {
    fetchInvestigationData();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Finding Investigation</h1>
            <p className="text-gray-600 mt-1">Loading investigation details...</p>
          </div>
        </div>
        <Card title="Investigation Details" subtitle="Security finding investigation">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Finding Investigation</h1>
            <p className="text-gray-600 mt-1">Investigation Details</p>
          </div>
          <Button onClick={handleBack} variant="secondary">
            Back to Findings
          </Button>
        </div>
        <Alert type="error" message={error} />
        <div className="flex justify-center">
          <Button onClick={handleRetry} variant="primary">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!data.finding) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Finding Investigation</h1>
            <p className="text-gray-600 mt-1">Investigation Details</p>
          </div>
          <Button onClick={handleBack} variant="secondary">
            Back to Findings
          </Button>
        </div>
        <Alert type="error" message="Finding not found" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Finding Investigation</h1>
          <p className="text-gray-600 mt-1">Security finding investigation and analysis</p>
        </div>
        <Button onClick={handleBack} variant="secondary">
          Back to Findings
        </Button>
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {/* Finding Summary */}
      <section aria-label="Finding summary">
        <FindingSummary
          finding={data.finding}
          loading={loading}
          error={error}
        />
      </section>

      {/* Detection Information */}
      <section aria-label="Detection information">
        <DetectionInfo
          detection={data.detection}
          loading={loading}
          error={error}
        />
      </section>

      {/* Evidence */}
      <section aria-label="Evidence and related events">
        <Evidence
          evidence={data.evidence}
          loading={loading}
          error={error}
        />
      </section>

      {/* AI Analysis */}
      <section aria-label="AI-assisted analysis">
        <AIAnalysisComponent
          aiAnalysis={data.aiAnalysis}
          loading={analysisLoading}
          error={analysisError}
          onRequestAnalysis={handleRequestAnalysis}
          canRequestAnalysis={!!data.finding}
        />
      </section>

      {/* Finding Status */}
      <section aria-label="Finding status management">
        <FindingStatus
          finding={data.finding}
          onStatusChange={handleStatusChange}
          loading={loading}
          error={error}
        />
      </section>

      {/* Status History */}
      <section aria-label="Status history">
        <StatusHistory
          statusHistory={data.statusHistory}
          loading={loading}
          error={error}
        />
      </section>
    </div>
  );
}