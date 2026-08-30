'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { apiClient, NetworkError, ServerError, AuthenticationError } from '@/lib/api';
import { Event, EventFilters } from '@/types';
import { safeText, safeDate, truncateText } from '@/lib/safe-rendering';

export default function EventsPage() {
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize] = useState(20);
  
  // Filter states
  const [filters, setFilters] = useState<EventFilters>({
    skip: 0,
    limit: pageSize
  });
  const [eventTypeFilter, setEventTypeFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [hostFilter, setHostFilter] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [startTimeFilter, setStartTimeFilter] = useState('');
  const [endTimeFilter, setEndTimeFilter] = useState('');

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const currentFilters: EventFilters = {
        ...filters,
        skip: currentPage * pageSize,
        limit: pageSize
      };
      
      if (eventTypeFilter) currentFilters.event_type = eventTypeFilter;
      if (sourceFilter) currentFilters.source = sourceFilter;
      if (hostFilter) currentFilters.host = hostFilter;
      if (userFilter) currentFilters.user = userFilter;
      if (startTimeFilter) currentFilters.start_time = startTimeFilter;
      if (endTimeFilter) currentFilters.end_time = endTimeFilter;
      
      const response = await apiClient.getEvents(currentFilters);
      setEvents(response.items || []);
      setTotal(response.total || 0);
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

  useEffect(() => {
    fetchEvents();
  }, [currentPage]);

  const handleApplyFilters = () => {
    setCurrentPage(0);
    fetchEvents();
  };

  const handleClearFilters = () => {
    setEventTypeFilter('');
    setSourceFilter('');
    setHostFilter('');
    setUserFilter('');
    setStartTimeFilter('');
    setEndTimeFilter('');
    setCurrentPage(0);
    setFilters({ skip: 0, limit: pageSize });
    fetchEvents();
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
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

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Events</h1>
          <p className="text-gray-600 mt-1">Security event stream and analysis</p>
        </div>
        {!loading && !error && (
          <div className="text-sm text-gray-600">
            {total} event{total !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {error && (
        <Alert type="error" message={error} />
      )}

      {/* Filters */}
      <Card title="Filters" subtitle="Filter events by criteria">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
              <Input
                value={eventTypeFilter}
                onChange={(e) => setEventTypeFilter(e.target.value)}
                placeholder="e.g., security, system"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
              <Input
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                placeholder="e.g., syslog, windows"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Host</label>
              <Input
                value={hostFilter}
                onChange={(e) => setHostFilter(e.target.value)}
                placeholder="e.g., server-01"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
              <Input
                value={userFilter}
                onChange={(e) => setUserFilter(e.target.value)}
                placeholder="e.g., john.doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
              <Input
                type="datetime-local"
                value={startTimeFilter}
                onChange={(e) => setStartTimeFilter(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
              <Input
                type="datetime-local"
                value={endTimeFilter}
                onChange={(e) => setEndTimeFilter(e.target.value)}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleApplyFilters} variant="primary">
              Apply Filters
            </Button>
            <Button onClick={handleClearFilters} variant="secondary">
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Events List */}
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
            <Button onClick={fetchEvents} variant="secondary">
              Refresh
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <div className="space-y-4">
            {events.map((event) => (
              <Card
                key={event.id}
                title={safeText(event.event_type)}
                subtitle={`Timestamp: ${safeDate(event.timestamp)}`}
              >
                <div className="space-y-3">
                  <div className="flex gap-2 flex-wrap">
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getEventTypeColor(event.event_type)}`}>
                      {safeText(event.event_type)}
                    </span>
                    <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {safeText(event.source)}
                    </span>
                    {event.host && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {safeText(event.host)}
                      </span>
                    )}
                    {event.user && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        {safeText(event.user)}
                      </span>
                    )}
                    {event.detection_id && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                        Detection: {safeText(event.detection_id)}
                      </span>
                    )}
                    {event.finding_id && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                        Finding: {safeText(event.finding_id)}
                      </span>
                    )}
                  </div>
                  {event.message && (
                    <p className="text-gray-600 text-sm">
                      {truncateText(event.message, 200)}
                    </p>
                  )}
                  <div className="flex gap-2">
                    <Button 
                      variant="primary" 
                      size="sm"
                      onClick={() => router.push(`/events/${event.id}`)}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <Button
                onClick={() => handlePageChange(currentPage - 1)}
                variant="secondary"
                size="sm"
                disabled={currentPage === 0}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {currentPage + 1} of {totalPages}
              </span>
              <Button
                onClick={() => handlePageChange(currentPage + 1)}
                variant="secondary"
                size="sm"
                disabled={currentPage >= totalPages - 1}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}