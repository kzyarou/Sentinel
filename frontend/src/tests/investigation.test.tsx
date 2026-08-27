import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FindingSummary } from '../components/investigation/FindingSummary';
import { DetectionInfo } from '../components/investigation/DetectionInfo';
import { Evidence } from '../components/investigation/Evidence';
import { AIAnalysis } from '../components/investigation/AIAnalysis';
import { FindingStatus } from '../components/investigation/FindingStatus';
import { StatusHistory } from '../components/investigation/StatusHistory';
import { Finding, Event, AIAnalysis as AIAnalysisType } from '../types';

// Mock FindingSummary tests
describe('FindingSummary', () => {
  const mockFinding: Finding = {
    id: '1',
    title: 'Test Finding',
    description: 'This is a test finding description',
    severity: 'HIGH',
    status: 'OPEN',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    category: 'Security',
    confidence: 0.85
  };

  it('renders finding summary correctly', () => {
    render(<FindingSummary finding={mockFinding} />);
    expect(screen.getByText('Test Finding')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('Open')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<FindingSummary finding={null} loading={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<FindingSummary finding={null} error="Test error" />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('shows empty state when no finding', () => {
    render(<FindingSummary finding={null} />);
    expect(screen.getByText('No finding data available')).toBeInTheDocument();
  });

  it('has proper ARIA labels for accessibility', () => {
    render(<FindingSummary finding={mockFinding} />);
    const severityBadge = screen.getByLabelText(/Severity: HIGH/i);
    const statusBadge = screen.getByLabelText(/Status: Open/i);
    expect(severityBadge).toBeInTheDocument();
    expect(statusBadge).toBeInTheDocument();
  });

  it('displays confidence percentage', () => {
    render(<FindingSummary finding={mockFinding} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });
});

// Mock DetectionInfo tests
describe('DetectionInfo', () => {
  const mockDetection = {
    id: '1',
    rule_name: 'Test Rule',
    rule_version: '1.0',
    severity: 'HIGH',
    confidence: 0.9,
    timestamp: '2024-01-01T00:00:00Z',
    rule_id: 'rule-1',
    rule_description: 'This is a test rule',
    matched_conditions: ['condition1', 'condition2'],
    metadata: { key: 'value' }
  };

  it('renders detection information correctly', () => {
    render(<DetectionInfo detection={mockDetection} />);
    expect(screen.getByText('Test Rule')).toBeInTheDocument();
    expect(screen.getByText('Version 1.0')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<DetectionInfo detection={null} loading={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<DetectionInfo detection={null} error="Test error" />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('displays detection metadata', () => {
    render(<DetectionInfo detection={mockDetection} />);
    expect(screen.getByText(/key/)).toBeInTheDocument();
  });

  it('has proper ARIA labels for accessibility', () => {
    render(<DetectionInfo detection={mockDetection} />);
    const severityBadge = screen.getByLabelText(/Detection severity: HIGH/i);
    expect(severityBadge).toBeInTheDocument();
  });
});

// Mock Evidence tests
describe('Evidence', () => {
  const mockEvents: Event[] = [
    {
      id: '1',
      event_type: 'security',
      source: 'system',
      timestamp: '2024-01-01T00:00:00Z',
      host: 'test-host',
      user: 'test-user',
      raw_data: { message: 'test' },
      normalized_data: { type: 'test' },
      finding_id: '1'
    }
  ];

  it('renders evidence list correctly', () => {
    render(<Evidence evidence={mockEvents} />);
    expect(screen.getByText(/security/i)).toBeInTheDocument();
    expect(screen.getByText('system')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<Evidence evidence={[]} loading={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no evidence', () => {
    render(<Evidence evidence={[]} />);
    expect(screen.getByText(/No additional evidence is associated with this finding/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<Evidence evidence={[]} error="Test error" />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('allows expanding event details', () => {
    render(<Evidence evidence={mockEvents} />);
    const expandButton = screen.getByRole('button');
    fireEvent.click(expandButton);
    expect(screen.getByText('Event Details')).toBeInTheDocument();
  });

  it('has proper keyboard navigation', () => {
    render(<Evidence evidence={mockEvents} />);
    const expandButton = screen.getByRole('button');
    expandButton.focus();
    fireEvent.keyDown(expandButton, { key: 'Enter' });
    expect(screen.getByText('Event Details')).toBeInTheDocument();
  });
});

// Mock AIAnalysis tests
describe('AIAnalysis', () => {
  const mockAIAnalysis: AIAnalysisType = {
    id: '1',
    finding_id: '1',
    analysis: 'Test analysis',
    confidence: 0.9,
    recommendations: ['Investigate further'],
    created_at: '2024-01-01T00:00:00Z',
    summary: 'Test summary',
    indicators: ['indicator1'],
    interpretation: 'Test interpretation',
    suggestions: ['suggestion1'],
    uncertainty_notes: ['note1'],
    model_used: 'test-model'
  };

  it('renders AI analysis correctly', () => {
    render(<AIAnalysis aiAnalysis={mockAIAnalysis} />);
    expect(screen.getByText('Test summary')).toBeInTheDocument();
    expect(screen.getByText('Test interpretation')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<AIAnalysis aiAnalysis={null} loading={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Processing AI analysis...')).toBeInTheDocument();
  });

  it('shows no analysis state', () => {
    const mockRequest = jest.fn();
    render(<AIAnalysis aiAnalysis={null} canRequestAnalysis={true} onRequestAnalysis={mockRequest} />);
    expect(screen.getByText(/No AI analysis has been generated yet/i)).toBeInTheDocument();
    expect(screen.getByText('Analyze with AI')).toBeInTheDocument();
  });

  it('calls onRequestAnalysis when button clicked', () => {
    const mockRequest = jest.fn();
    render(<AIAnalysis aiAnalysis={null} canRequestAnalysis={true} onRequestAnalysis={mockRequest} />);
    const button = screen.getByText('Analyze with AI');
    fireEvent.click(button);
    expect(mockRequest).toHaveBeenCalled();
  });

  it('shows error state with retry option', () => {
    const mockRequest = jest.fn();
    render(<AIAnalysis aiAnalysis={null} error="Test error" canRequestAnalysis={true} onRequestAnalysis={mockRequest} />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
    expect(screen.getByText('Retry Analysis')).toBeInTheDocument();
  });

  it('displays advisory notice for AI content', () => {
    render(<AIAnalysis aiAnalysis={mockAIAnalysis} />);
    expect(screen.getByText(/AI-Generated Content/i)).toBeInTheDocument();
    expect(screen.getByText(/advisory/i)).toBeInTheDocument();
  });

  it('displays confidence score with progress bar', () => {
    render(<AIAnalysis aiAnalysis={mockAIAnalysis} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '90');
  });
});

// Mock FindingStatus tests
describe('FindingStatus', () => {
  const mockFinding: Finding = {
    id: '1',
    title: 'Test Finding',
    description: 'Test description',
    severity: 'HIGH',
    status: 'OPEN',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z'
  };

  it('renders current status correctly', () => {
    render(<FindingStatus finding={mockFinding} onStatusChange={jest.fn()} />);
    expect(screen.getByText('Open')).toBeInTheDocument();
    expect(screen.getByText('Finding requires investigation')).toBeInTheDocument();
  });

  it('shows valid status transitions', () => {
    render(<FindingStatus finding={mockFinding} onStatusChange={jest.fn()} />);
    expect(screen.getByText('Investigating')).toBeInTheDocument();
    expect(screen.getByText('Resolved')).toBeInTheDocument();
    expect(screen.getByText('False Positive')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<FindingStatus finding={null} loading={true} onStatusChange={jest.fn()} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows confirmation dialog when status change requested', () => {
    render(<FindingStatus finding={mockFinding} onStatusChange={jest.fn()} />);
    const investigatingButton = screen.getByText('Investigating');
    fireEvent.click(investigatingButton);
    expect(screen.getByText(/Confirm Status Change/i)).toBeInTheDocument();
  });

  it('calls onStatusChange when confirmed', () => {
    const mockStatusChange = jest.fn();
    render(<FindingStatus finding={mockFinding} onStatusChange={mockStatusChange} />);
    const investigatingButton = screen.getByText('Investigating');
    fireEvent.click(investigatingButton);
    const confirmButton = screen.getByText('Confirm Change');
    fireEvent.click(confirmButton);
    expect(mockStatusChange).toHaveBeenCalledWith('INVESTIGATING');
  });

  it('cancels status change when cancel clicked', () => {
    render(<FindingStatus finding={mockFinding} onStatusChange={jest.fn()} />);
    const investigatingButton = screen.getByText('Investigating');
    fireEvent.click(investigatingButton);
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    expect(screen.queryByText(/Confirm Status Change/i)).not.toBeInTheDocument();
  });

  it('has proper ARIA labels for accessibility', () => {
    render(<FindingStatus finding={mockFinding} onStatusChange={jest.fn()} />);
    const currentStatusBadge = screen.getByLabelText(/Current status: Open/i);
    expect(currentStatusBadge).toBeInTheDocument();
  });
});

// Mock StatusHistory tests
describe('StatusHistory', () => {
  const mockHistory = [
    {
      id: '1',
      status: 'INVESTIGATING',
      previous_status: 'OPEN',
      timestamp: '2024-01-01T00:00:00Z',
      actor: 'test-user',
      reason: 'Investigation started'
    },
    {
      id: '2',
      status: 'OPEN',
      timestamp: '2024-01-01T00:00:00Z',
      actor: 'system',
      reason: 'Finding created'
    }
  ];

  it('renders status history correctly', () => {
    render(<StatusHistory statusHistory={mockHistory} />);
    expect(screen.getByText('Investigating')).toBeInTheDocument();
    expect(screen.getByText('Open')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<StatusHistory statusHistory={[]} loading={true} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows empty state when no history', () => {
    render(<StatusHistory statusHistory={[]} />);
    expect(screen.getByText(/No status history available/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(<StatusHistory statusHistory={[]} error="Test error" />);
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('displays timeline correctly', () => {
    render(<StatusHistory statusHistory={mockHistory} />);
    expect(screen.getByText('Investigation started')).toBeInTheDocument();
    expect(screen.getByText('Finding created')).toBeInTheDocument();
  });

  it('displays actor information', () => {
    render(<StatusHistory statusHistory={mockHistory} />);
    expect(screen.getByText(/Changed by: test-user/i)).toBeInTheDocument();
  });

  it('has proper ARIA labels for status badges', () => {
    render(<StatusHistory statusHistory={mockHistory} />);
    const investigatingBadge = screen.getByLabelText(/New status: Investigating/i);
    const openBadge = screen.getByLabelText(/Previous status: Open/i);
    expect(investigatingBadge).toBeInTheDocument();
    expect(openBadge).toBeInTheDocument();
  });
});