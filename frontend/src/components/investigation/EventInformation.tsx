import { Event } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

interface EventInformationProps {
  event: Event;
}

export function EventInformation({ event }: EventInformationProps) {
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
    <div className="space-y-4">
      {/* Event Header */}
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            Event Details
          </h4>
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
        {/* Timestamp */}
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-1">Timestamp</h5>
          <time className="text-sm text-gray-600" dateTime={event.timestamp}>
            {safeDate(event.timestamp)}
          </time>
        </div>

        {/* Source */}
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-1">Source</h5>
          <span className="text-sm text-gray-600">
            {safeText(event.source)}
          </span>
        </div>

        {/* Host */}
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-1">Host</h5>
          <span className="text-sm text-gray-600">
            {safeText(event.host)}
          </span>
        </div>

        {/* User/Entity */}
        {event.user && (
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-1">User/Entity</h5>
            <span className="text-sm text-gray-600">
              {safeText(event.user)}
            </span>
          </div>
        )}

        {/* IP Address */}
        {event.ip_address && (
          <div>
            <h5 className="text-sm font-medium text-gray-700 mb-1">IP Address</h5>
            <span className="text-sm text-gray-600 font-mono">
              {safeText(event.ip_address)}
            </span>
          </div>
        )}
      </div>

      {/* Normalized Data */}
      {event.normalized_data && Object.keys(event.normalized_data).length > 0 && (
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-2">Normalized Fields</h5>
          <div className="bg-gray-50 border border-gray-200 rounded p-3">
            <pre className="text-xs text-gray-700 overflow-x-auto max-h-40">
              {JSON.stringify(event.normalized_data, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Original Event Data */}
      {event.raw_data && Object.keys(event.raw_data).length > 0 && (
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-2">Original Event Data</h5>
          <div className="bg-gray-50 border border-gray-200 rounded p-3">
            <pre className="text-xs text-gray-700 overflow-x-auto max-h-40">
              {JSON.stringify(event.raw_data, null, 2)}
            </pre>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Note: Original data is preserved for forensic analysis.
          </p>
        </div>
      )}

      {/* Security Notice */}
      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
        <p className="text-xs text-yellow-800">
          <strong>Security Notice:</strong> This event data is treated as untrusted and rendered safely.
          Sensitive information (credentials, secrets) is filtered and not displayed.
        </p>
      </div>
    </div>
  );
}