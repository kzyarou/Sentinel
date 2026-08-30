import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EventsPage from '../app/events/page';
import EventDetailPage from '../app/events/[id]/page';
import { Event } from '../types';

// Mock the API client
jest.mock('../lib/api', () => ({
  apiClient: {
    getEvents: jest.fn(),
    getEvent: jest.fn(),
  },
  NetworkError: class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'NetworkError';
    }
  },
  ServerError: class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'ServerError';
    }
  },
  AuthenticationError: class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'AuthenticationError';
    }
  },
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}));

const { apiClient } = require('../lib/api');
const { useRouter, useParams } = require('next/navigation');

// Mock EventsPage tests
describe('EventsPage', () => {
  const mockEvents: Event[] = [
    {
      id: '1',
      event_type: 'security',
      source: 'syslog',
      timestamp: '2024-01-01T00:00:00Z',
      host: 'server-01',
      user: 'john.doe',
      ip_address: '192.168.1.1',
      raw_data: { message: 'test' },
      normalized_data: { type: 'test' },
      detection_id: 'det-1',
      finding_id: 'find-1',
      message: 'Test security event'
    },
    {
      id: '2',
      event_type: 'system',
      source: 'windows',
      timestamp: '2024-01-01T01:00:00Z',
      host: 'server-02',
      raw_data: { message: 'test2' },
      normalized_data: { type: 'test2' }
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: jest.fn(),
    });
  });

  it('renders events list correctly', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: mockEvents,
      total: 2,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('Security Events')).toBeInTheDocument();
      expect(screen.getByText('2 events')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    (apiClient.getEvents as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<EventsPage />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no events', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: [],
      total: 0,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('No security events found')).toBeInTheDocument();
    });
  });

  it('shows error state', async () => {
    (apiClient.getEvents as jest.Mock).mockRejectedValue(
      new Error('Network error')
    );

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch events/i)).toBeInTheDocument();
    });
  });

  it('applies filters correctly', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: mockEvents,
      total: 2,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('Security Events')).toBeInTheDocument();
    });

    const eventTypeInput = screen.getByPlaceholderText('e.g., security, system');
    fireEvent.change(eventTypeInput, { target: { value: 'security' } });

    const applyButton = screen.getByText('Apply Filters');
    fireEvent.click(applyButton);

    expect(apiClient.getEvents).toHaveBeenCalledWith(
      expect.objectContaining({
        event_type: 'security',
        skip: 0,
        limit: 20
      })
    );
  });

  it('clears filters correctly', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: mockEvents,
      total: 2,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('Security Events')).toBeInTheDocument();
    });

    const clearButton = screen.getByText('Clear Filters');
    fireEvent.click(clearButton);

    expect(apiClient.getEvents).toHaveBeenCalledWith(
      expect.objectContaining({
        skip: 0,
        limit: 20
      })
    );
  });

  it('handles pagination correctly', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: mockEvents,
      total: 40,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 2')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    expect(apiClient.getEvents).toHaveBeenCalledWith(
      expect.objectContaining({
        skip: 20,
        limit: 20
      })
    );
  });

  it('displays related detection and finding badges', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: [mockEvents[0]],
      total: 1,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText(/Detection: det-1/i)).toBeInTheDocument();
      expect(screen.getByText(/Finding: find-1/i)).toBeInTheDocument();
    });
  });

  it('navigates to event detail on View Details click', async () => {
    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: [mockEvents[0]],
      total: 1,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      expect(screen.getByText('View Details')).toBeInTheDocument();
    });

    const viewDetailsButton = screen.getByText('View Details');
    fireEvent.click(viewDetailsButton);

    expect(mockPush).toHaveBeenCalledWith('/events/1');
  });

  it('has proper ARIA labels for accessibility', async () => {
    (apiClient.getEvents as jest.Mock).mockResolvedValue({
      items: [mockEvents[0]],
      total: 1,
      skip: 0,
      limit: 20
    });

    render(<EventsPage />);

    await waitFor(() => {
      const eventTypeBadge = screen.getByLabelText(/Event type: security/i);
      expect(eventTypeBadge).toBeInTheDocument();
    });
  });
});

// Mock EventDetailPage tests
describe('EventDetailPage', () => {
  const mockEvent: Event = {
    id: '1',
    event_type: 'security',
    source: 'syslog',
    timestamp: '2024-01-01T00:00:00Z',
    host: 'server-01',
    user: 'john.doe',
    ip_address: '192.168.1.1',
    raw_data: { message: 'test', sensitive: 'should-be-filtered' },
    normalized_data: { type: 'test', processed: true },
    detection_id: 'det-1',
    finding_id: 'find-1',
    message: 'Test security event',
    ingestion_timestamp: '2024-01-01T00:01:00Z',
    metadata: { source_ip: '192.168.1.1', correlation_id: 'abc123' }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: jest.fn(),
    });
    (useParams as jest.Mock).mockReturnValue({ id: '1' });
  });

  it('renders event details correctly', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Event Details')).toBeInTheDocument();
      expect(screen.getByText('security')).toBeInTheDocument();
      expect(screen.getByText('syslog')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    (apiClient.getEvent as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<EventDetailPage />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state for not found', async () => {
    const NotFoundError = class extends Error {
      constructor(message: string) {
        super(message);
        this.name = 'NotFoundError';
      }
    };

    (apiClient.getEvent as jest.Mock).mockRejectedValue(
      new NotFoundError('Event not found')
    );

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Event not found/i)).toBeInTheDocument();
    });
  });

  it('shows error state for unauthorized', async () => {
    const AuthorizationError = class extends Error {
      constructor(message: string) {
        super(message);
        this.name = 'AuthorizationError';
      }
    };

    (apiClient.getEvent as jest.Mock).mockRejectedValue(
      new AuthorizationError('Unauthorized')
    );

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText(/You do not have permission/i)).toBeInTheDocument();
    });
  });

  it('displays normalized event data', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Normalized Event Data')).toBeInTheDocument();
      expect(screen.getByText(/"type": "test"/i)).toBeInTheDocument();
    });
  });

  it('toggles raw event data display', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Raw Event Data')).toBeInTheDocument();
    });

    const showButton = screen.getByText('Show Raw Data');
    fireEvent.click(showButton);

    expect(screen.getByText('Hide Raw Data')).toBeInTheDocument();
    expect(screen.getByText(/"message": "test"/i)).toBeInTheDocument();
  });

  it('displays event metadata', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Event Metadata')).toBeInTheDocument();
      expect(screen.getByText(/"correlation_id": "abc123"/i)).toBeInTheDocument();
    });
  });

  it('displays traceability information', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Traceability')).toBeInTheDocument();
      expect(screen.getByText(/Event → Normalization → Detection → Finding/i)).toBeInTheDocument();
    });
  });

  it('navigates to related detection', async () => {
    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('View Detection')).toBeInTheDocument();
    });

    const viewDetectionButton = screen.getByText('View Detection');
    fireEvent.click(viewDetectionButton);

    expect(mockPush).toHaveBeenCalledWith('/detections/det-1');
  });

  it('navigates to related finding', async () => {
    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('View Finding')).toBeInTheDocument();
    });

    const viewFindingButton = screen.getByText('View Finding');
    fireEvent.click(viewFindingButton);

    expect(mockPush).toHaveBeenCalledWith('/findings/find-1');
  });

  it('shows security notice for raw data', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Security Notice/i)).toBeInTheDocument();
      expect(screen.getByText(/treated as untrusted/i)).toBeInTheDocument();
    });
  });

  it('navigates back to events list', async () => {
    const mockPush = jest.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Back to Events')).toBeInTheDocument();
    });

    const backButton = screen.getByText('Back to Events');
    fireEvent.click(backButton);

    expect(mockPush).toHaveBeenCalledWith('/events');
  });

  it('has proper ARIA labels for accessibility', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      const eventTypeBadge = screen.getByLabelText(/Event type: security/i);
      expect(eventTypeBadge).toBeInTheDocument();
    });
  });

  it('displays ingestion timestamp when available', async () => {
    (apiClient.getEvent as jest.Mock).mockResolvedValue(mockEvent);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Ingestion Timestamp')).toBeInTheDocument();
    });
  });

  it('hides related resources when none available', async () => {
    const eventWithoutRelations = { ...mockEvent, detection_id: undefined, finding_id: undefined };
    (apiClient.getEvent as jest.Mock).mockResolvedValue(eventWithoutRelations);

    render(<EventDetailPage />);

    await waitFor(() => {
      expect(screen.getByText(/No related detections or findings/i)).toBeInTheDocument();
    });
  });
});