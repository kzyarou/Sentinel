import { useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { Event } from '@/types';
import { EventInformation } from './EventInformation';

interface EvidenceProps {
  evidence: Event[];
  loading?: boolean;
  error?: string | null;
}

export function Evidence({ evidence, loading = false, error = null }: EvidenceProps) {
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  const toggleEventExpansion = (eventId: string) => {
    setExpandedEventId(expandedEventId === eventId ? null : eventId);
  };

  if (loading) {
    return (
      <Card title="Evidence" subtitle="Related events and evidence">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Evidence" subtitle="Related events and evidence">
        <Alert type="error" message={error} />
      </Card>
    );
  }

  if (!evidence || evidence.length === 0) {
    return (
      <Card title="Evidence" subtitle="Related events and evidence">
        <div className="text-center py-8 text-gray-500">
          <p className="mb-4">No additional evidence is associated with this finding.</p>
          <p className="text-sm text-gray-400">
            Evidence will appear here when related events are linked to this finding.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card title="Evidence" subtitle="Related events and evidence">
      <div className="space-y-4">
        {/* Evidence Tracing Header */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded">
          <h4 className="text-sm font-medium text-blue-900 mb-1">Evidence Tracing</h4>
          <p className="text-xs text-blue-800">
            This section displays the evidence chain: Finding → Detection → Evidence → Original Event
          </p>
        </div>

        {/* Evidence List */}
        <div className="space-y-3">
          {evidence.map((event, index) => (
            <div key={event.id} className="border border-gray-200 rounded overflow-hidden">
              {/* Event Summary (Collapsible) */}
              <div className="p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                   onClick={() => toggleEventExpansion(event.id)}
                   role="button"
                   tabIndex={0}
                   aria-expanded={expandedEventId === event.id}
                   onKeyPress={(e) => {
                     if (e.key === 'Enter' || e.key === ' ') {
                       e.preventDefault();
                       toggleEventExpansion(event.id);
                     }
                   }}>
                <div className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500">
                        #{index + 1}
                      </span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        {event.event_type}
                      </span>
                      <span className="text-xs text-gray-600">
                        {event.source}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <time dateTime={event.timestamp}>
                        {new Date(event.timestamp).toLocaleString()}
                      </time>
                      {event.host && (
                        <>
                          <span aria-hidden="true">•</span>
                          <span>{event.host}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className="text-gray-400 transform transition-transform">
                      {expandedEventId === event.id ? '▼' : '▶'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Expanded Event Details */}
              {expandedEventId === event.id && (
                <div className="p-4 border-t border-gray-200">
                  <EventInformation event={event} />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Evidence Summary */}
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded">
          <p className="text-xs text-gray-700">
            <strong>Evidence Summary:</strong> {evidence.length} event{evidence.length !== 1 ? 's' : ''} 
            {' '}linked to this finding. Expand each event to view detailed information and trace back to the original data.
          </p>
        </div>
      </div>
    </Card>
  );
}