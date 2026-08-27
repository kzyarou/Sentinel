'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib/api';
import { Event } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getEvents();
        setEvents(response.items || []);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view events.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch events. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

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

  const handleRetry = () => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getEvents();
        setEvents(response.items || []);
      } catch (err) {
        if (err instanceof NetworkError) {
          setError('Unable to connect to the backend server. Please check if the backend is running.');
        } else if (err instanceof AuthenticationError) {
          setError('Authentication required. Please log in to view events.');
        } else if (err instanceof ServerError) {
          setError('Backend server error. Please try again later.');
        } else {
          setError('Failed to fetch events. Please try again.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Events</h1>
          <p className="text-gray-600 mt-1">Security event stream and analysis</p>
        </div>
        {!loading && !error && events.length > 0 && (
          <div className="text-sm text-gray-600">
            {events.length} event{events.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {loading ? (
        <Card title="Security Events" subtitle="View security event logs">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
      ) : events.length === 0 ? (
        <Card title="Security Events" subtitle="View security event logs">
          <div className="text-center py-8">
            <div className="text-gray-500 mb-4">No security events found</div>
            <Button onClick={handleRetry} variant="secondary">
              Refresh
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {events.map((event) => (
            <Card
              key={event.id}
              title={safeText(event.event_type)}
              subtitle={`Timestamp: ${safeDate(event.timestamp)}`}
            >
              <div className="space-y-3">
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getEventTypeColor(event.event_type)}`}>
                    {safeText(event.event_type)}
                  </span>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {safeText(event.source)}
                  </span>
                </div>
                <p className="text-gray-600 text-sm">
                  {truncateText(event.message, 200)}
                </p>
                <div className="flex gap-2">
                  <Button variant="primary" size="sm">
                    View Details
                  </Button>
                  <Button variant="secondary" size="sm">
                    Create Finding
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