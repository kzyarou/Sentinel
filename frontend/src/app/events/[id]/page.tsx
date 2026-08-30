'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError, AuthorizationError, NotFoundError } from '@/lib/api';
import { Event } from '@/types';
import { safeText, safeDate } from '@/lib/safe-rendering';

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;
  
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRawData, setShowRawData] = useState(false);

  const fetchEvent = async () => {
    try {
      setLoading(true);
      setError(null);
      const eventData = await apiClient.getEvent(eventId);
      setEvent(eventData);
    } catch (err) {
      if (err instanceof NotFoundError) {
        setError('Event not found. It may have been deleted or you may not have access.');
      } else if (err instanceof AuthorizationError) {
        setError('You do not have permission to view this event.');
      } else if (err instanceof AuthenticationError) {
        setError('Authentication required. Please log in to view this event.');
      } else if (err instanceof NetworkError) {
        setError('Unable to connect to the backend server. Please check if the backend is running.');
      } else if (err instanceof ServerError) {
        setError('Backend server error. Please try again later.');
      } else {
        setError('Failed to fetch event details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (eventId) {
      fetchEvent();
    }
  }, [eventId]);

  const handleBack = () => {
    router.push('/events');
  };

  const handleNavigateToDetection = (detectionId: string) => {
    // Navigate to detection details when detection page is implemented
    router.push(`/detections/${detectionId}`);
  };

  const handleNavigateToFinding = (findingId: string) => {
    router.push(`/findings/${findingId}`);
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Event Details</h1>
            <p className="text-gray-600 mt-1">Loading event information...</p>
          </div>
        </div>
        <Card title="Event Information" subtitle="Security event details">
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
            <h1 className="text-3xl font-bold text-gray-900">Event Details</h1>
            <p className="text-gray-600 mt-1">Event Information</p>
          </div>
          <Button onClick={handleBack} variant="secondary">
            Back to Events
          </Button>
        </div>
        <Alert type="error" message={error} />
        <div className="flex justify-center">
          <Button onClick={fetchEvent} variant="primary">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Event Details</h1>
            <p className="text-gray-600 mt-1">Event Information</p>
          </div>
          <Button onClick={handleBack} variant="secondary">
            Back to Events
          </Button>
        </div>
        <Alert type="error" message="Event not found" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Event Details</h1>
          <p className="text-gray-600 mt-1">Security event information and analysis</p>
        </div>
        <Button onClick={handleBack} variant="secondary">
          Back to Events
        </Button>
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {/* Event Summary */}
      <section aria-label="Event summary">
        <Card title="Event Summary" subtitle="Overview of the security event">
          <div className="space-y-4">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {safeText(event.event_type)}
                </h3>
                <div className="flex gap-2 flex-wrap">
                  <span 
                    className={`px-2 py-1 rounded text-xs font-medium border ${getEventTypeColor(event.event_type)}`}
                    aria-label={`Event type: ${safeText(event.event_type)}`}
                  >
                    {safeText(event.event_type)}
                  </span>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {safeText(event.source)}
                  </span>
                </div>
              </div>
            </div>

            {/* Key Information Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Event ID</h4>
                <span className="text-sm text-gray-600 font-mono">
                  {safeText(event.id)}
                </span>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Timestamp</h4>
                <time className="text-sm text-gray-600" dateTime={event.timestamp}>
                  {safeDate(event.timestamp)}
                </time>
              </div>
              {event.ingestion_timestamp && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Ingestion Timestamp</h4>
                  <time className="text-sm text-gray-600" dateTime={event.ingestion_timestamp}>
                    {safeDate(event.ingestion_timestamp)}
                  </time>
                </div>
              )}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Host</h4>
                <span className="text-sm text-gray-600">
                  {safeText(event.host)}
                </span>
              </div>
              {event.user && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">User/Entity</h4>
                  <span className="text-sm text-gray-600">
                    {safeText(event.user)}
                  </span>
                </div>
              )}
              {event.ip_address && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">IP Address</h4>
                  <span className="text-sm text-gray-600 font-mono">
                    {safeText(event.ip_address)}
                  </span>
                </div>
              )}
            </div>

            {/* Related Resources */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Related Resources</h4>
              <div className="flex gap-2 flex-wrap">
                {event.detection_id && (
                  <Button
                    onClick={() => handleNavigateToDetection(event.detection_id!)}
                    variant="secondary"
                    size="sm"
                  >
                    View Detection
                  </Button>
                )}
                {event.finding_id && (
                  <Button
                    onClick={() => handleNavigateToFinding(event.finding_id!)}
                    variant="primary"
                    size="sm"
                  >
                    View Finding
                  </Button>
                )}
                {!event.detection_id && !event.finding_id && (
                  <span className="text-sm text-gray-500">
                    No related detections or findings
                  </span>
                )}
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* Normalized Event Data */}
      {event.normalized_data && Object.keys(event.normalized_data).length > 0 && (
        <section aria-label="Normalized event data">
          <Card title="Normalized Event Data" subtitle="Processed event information">
            <div className="space-y-4">
              <div className="bg-gray-50 border border-gray-200 rounded p-3">
                <pre className="text-xs text-gray-700 overflow-x-auto max-h-96">
                  {JSON.stringify(event.normalized_data, null, 2)}
                </pre>
              </div>
              <p className="text-xs text-gray-500">
                Normalized data represents the processed event information used by Sentinel's detection engine.
              </p>
            </div>
          </Card>
        </section>
      )}

      {/* Raw Event Data */}
      {event.raw_data && Object.keys(event.raw_data).length > 0 && (
        <section aria-label="Raw event data">
          <Card title="Raw Event Data" subtitle="Original telemetry from source">
            <div className="space-y-4">
              {/* Security Notice */}
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-xs text-yellow-800">
                  <strong>Security Notice:</strong> Raw event data originates from external telemetry sources.
                  This data is treated as untrusted and rendered safely. Credentials and secrets are filtered where possible.
                </p>
              </div>

              {/* Toggle Button */}
              <Button
                onClick={() => setShowRawData(!showRawData)}
                variant="secondary"
                size="sm"
              >
                {showRawData ? 'Hide Raw Data' : 'Show Raw Data'}
              </Button>

              {/* Raw Data Display */}
              {showRawData && (
                <div className="bg-gray-50 border border-gray-200 rounded p-3">
                  <pre className="text-xs text-gray-700 overflow-x-auto max-h-96">
                    {JSON.stringify(event.raw_data, null, 2)}
                  </pre>
                </div>
              )}

              <p className="text-xs text-gray-500">
                Original event data is preserved for forensic analysis and compliance requirements.
              </p>
            </div>
          </Card>
        </section>
      )}

      {/* Event Metadata */}
      {event.metadata && Object.keys(event.metadata).length > 0 && (
        <section aria-label="Event metadata">
          <Card title="Event Metadata" subtitle="Additional event information">
            <div className="space-y-4">
              <div className="bg-gray-50 border border-gray-200 rounded p-3">
                <pre className="text-xs text-gray-700 overflow-x-auto max-h-96">
                  {JSON.stringify(event.metadata, null, 2)}
                </pre>
              </div>
              <p className="text-xs text-gray-500">
                Metadata contains additional information about the event that may be useful for investigation.
              </p>
            </div>
          </Card>
        </section>
      )}

      {/* Traceability Information */}
      <section aria-label="Traceability information">
        <Card title="Traceability" subtitle="Event relationship chain">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium text-gray-700">Event</span>
              <span className="text-gray-400">→</span>
              <span className="font-medium text-gray-700">Normalization</span>
              <span className="text-gray-400">→</span>
              <span className="font-medium text-gray-700">Detection</span>
              <span className="text-gray-400">→</span>
              <span className="font-medium text-gray-700">Finding</span>
            </div>
            <p className="text-xs text-gray-600">
              This event is part of the security investigation chain. Use the related resource buttons above
              to navigate through the detection and finding processes.
            </p>
          </div>
        </Card>
      </section>
    </div>
  );
}