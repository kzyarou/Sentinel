import { render, screen } from '@testing-library/react';
import { MetricsCard } from '@/components/dashboard/MetricsCard';
import { SeverityMetrics } from '@/components/dashboard/SeverityMetrics';
import { RecentFindings } from '@/components/dashboard/RecentFindings';
import { SystemHealth } from '@/components/dashboard/SystemHealth';
import { DashboardRefresh } from '@/components/dashboard/DashboardRefresh';
import { DashboardKeyboardNav } from '@/components/dashboard/DashboardKeyboardNav';

describe('Dashboard Components', () => {
  describe('MetricsCard', () => {
    it('should render metrics card with title and value', () => {
      render(
        <MetricsCard
          title="Test Title"
          subtitle="Test Subtitle"
          value={42}
          color="text-blue-600"
          ariaLabel="42 test items"
        />
      );

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('should render icon when provided', () => {
      render(
        <MetricsCard
          title="Test Title"
          subtitle="Test Subtitle"
          value={42}
          color="text-blue-600"
          icon="📊"
          ariaLabel="42 test items"
        />
      );

      expect(screen.getByText('📊')).toBeInTheDocument();
    });

    it('should have correct aria-label for accessibility', () => {
      render(
        <MetricsCard
          title="Test Title"
          subtitle="Test Subtitle"
          value={42}
          color="text-blue-600"
          ariaLabel="42 test items"
        />
      );

      const valueElement = screen.getByText('42');
      expect(valueElement).toHaveAttribute('aria-label', '42 test items');
    });
  });

  describe('SeverityMetrics', () => {
    it('should render severity metrics correctly', () => {
      render(
        <SeverityMetrics
          critical={5}
          high={10}
          medium={15}
          low={20}
          total={50}
        />
      );

      expect(screen.getByText('Critical')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('High')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
      expect(screen.getByText('Medium')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('Total')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
    });

    it('should render loading state', () => {
      render(
        <SeverityMetrics
          critical={0}
          high={0}
          medium={0}
          low={0}
          total={0}
          loading={true}
        />
      );

      expect(screen.getByLabelText('Loading metrics')).toBeInTheDocument();
    });

    it('should display severity icons', () => {
      render(
        <SeverityMetrics
          critical={5}
          high={10}
          medium={15}
          low={20}
          total={50}
        />
      );

      expect(screen.getByText('🔴')).toBeInTheDocument();
      expect(screen.getByText('🟠')).toBeInTheDocument();
      expect(screen.getByText('🟡')).toBeInTheDocument();
      expect(screen.getByText('📊')).toBeInTheDocument();
    });
  });

  describe('RecentFindings', () => {
    const mockFindings = [
      {
        id: '1',
        title: 'Test Finding 1',
        description: 'Test description 1',
        severity: 'HIGH' as const,
        status: 'OPEN' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '2',
        title: 'Test Finding 2',
        description: 'Test description 2',
        severity: 'CRITICAL' as const,
        status: 'IN_PROGRESS' as const,
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z'
      }
    ];

    it('should render recent findings', () => {
      render(<RecentFindings findings={mockFindings} />);

      expect(screen.getByText('Test Finding 1')).toBeInTheDocument();
      expect(screen.getByText('Test Finding 2')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
    });

    it('should render loading state', () => {
      render(<RecentFindings findings={[]} loading={true} />);

      expect(screen.getByLabelText('Loading recent findings')).toBeInTheDocument();
    });

    it('should render error state', () => {
      render(<RecentFindings findings={[]} error="Failed to load" />);

      expect(screen.getByText('Failed to load recent findings')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should render empty state', () => {
      render(<RecentFindings findings={[]} />);

      expect(screen.getByText('No findings require attention')).toBeInTheDocument();
    });

    it('should limit number of findings displayed', () => {
      render(<RecentFindings findings={mockFindings} maxItems={1} />);

      expect(screen.getByText('Test Finding 1')).toBeInTheDocument();
      expect(screen.queryByText('Test Finding 2')).not.toBeInTheDocument();
    });

    it('should show view all link when findings exceed max items', () => {
      render(<RecentFindings findings={mockFindings} maxItems={1} />);

      expect(screen.getByText('View all 2 findings')).toBeInTheDocument();
    });
  });

  describe('SystemHealth', () => {
    const mockHealthData = {
      api: { status: 'healthy' as const, lastCheck: '2024-01-01T00:00:00Z' },
      database: { status: 'degraded' as const, lastCheck: '2024-01-01T00:00:00Z' },
      detectionEngine: { status: 'unavailable' as const, lastCheck: '2024-01-01T00:00:00Z' }
    };

    it('should render system health components', () => {
      render(<SystemHealth healthData={mockHealthData} />);

      expect(screen.getByText('API')).toBeInTheDocument();
      expect(screen.getByText('Database')).toBeInTheDocument();
      expect(screen.getByText('Detection Engine')).toBeInTheDocument();
    });

    it('should render loading state', () => {
      render(<SystemHealth healthData={mockHealthData} loading={true} />);

      expect(screen.getByLabelText('Loading system health')).toBeInTheDocument();
    });

    it('should render error state', () => {
      render(<SystemHealth healthData={mockHealthData} error="Failed to load" />);

      expect(screen.getByText('Failed to load system health')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should display correct status labels', () => {
      render(<SystemHealth healthData={mockHealthData} />);

      expect(screen.getByText('Healthy')).toBeInTheDocument();
      expect(screen.getByText('Degraded')).toBeInTheDocument();
      expect(screen.getByText('Unavailable')).toBeInTheDocument();
    });

    it('should have proper aria-labels for accessibility', () => {
      render(<SystemHealth healthData={mockHealthData} />);

      const apiStatus = screen.getByLabelText(/API status:/);
      expect(apiStatus).toBeInTheDocument();
    });
  });

  describe('DashboardRefresh', () => {
    it('should render refresh button', () => {
      const mockRefresh = jest.fn();
      render(<DashboardRefresh onRefresh={mockRefresh} />);

      expect(screen.getByLabelText('Refresh dashboard data')).toBeInTheDocument();
    });

    it('should call onRefresh when button is clicked', () => {
      const mockRefresh = jest.fn();
      render(<DashboardRefresh onRefresh={mockRefresh} />);

      const button = screen.getByLabelText('Refresh dashboard data');
      button.click();

      expect(mockRefresh).toHaveBeenCalledTimes(1);
    });

    it('should show loading state when isLoading is true', () => {
      const mockRefresh = jest.fn();
      render(<DashboardRefresh onRefresh={mockRefresh} isLoading={true} />);

      expect(screen.getByText('Refreshing...')).toBeInTheDocument();
    });

    it('should show last refresh time when provided', () => {
      const mockRefresh = jest.fn();
      const lastRefresh = new Date('2024-01-01T12:00:00Z');
      render(<DashboardRefresh onRefresh={mockRefresh} lastRefresh={lastRefresh} />);

      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    });

    it('should render auto-refresh toggle when onToggleAutoRefresh is provided', () => {
      const mockRefresh = jest.fn();
      const mockToggle = jest.fn();
      render(
        <DashboardRefresh
          onRefresh={mockRefresh}
          onToggleAutoRefresh={mockToggle}
          autoRefresh={false}
        />
      );

      expect(screen.getByLabelText('Enable auto refresh')).toBeInTheDocument();
    });

    it('should have proper aria attributes for accessibility', () => {
      const mockRefresh = jest.fn();
      render(<DashboardRefresh onRefresh={mockRefresh} isLoading={true} />);

      const button = screen.getByLabelText('Refresh dashboard data');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('DashboardKeyboardNav', () => {
    it('should not render anything (invisible component)', () => {
      const mockRefresh = jest.fn();
      const { container } = render(<DashboardKeyboardNav onRefresh={mockRefresh} />);

      expect(container.firstChild).toBeNull();
    });

    it('should call onRefresh when Ctrl+R is pressed', () => {
      const mockRefresh = jest.fn();
      render(<DashboardKeyboardNav onRefresh={mockRefresh} />);

      const event = new KeyboardEvent('keydown', { ctrlKey: true, key: 'r' });
      window.dispatchEvent(event);

      expect(mockRefresh).toHaveBeenCalledTimes(1);
    });

    it('should call onNavigateToFindings when Alt+F is pressed', () => {
      const mockNavigate = jest.fn();
      render(<DashboardKeyboardNav onNavigateToFindings={mockNavigate} />);

      const event = new KeyboardEvent('keydown', { altKey: true, key: 'f' });
      window.dispatchEvent(event);

      expect(mockNavigate).toHaveBeenCalledTimes(1);
    });

    it('should call onNavigateToEvents when Alt+E is pressed', () => {
      const mockNavigate = jest.fn();
      render(<DashboardKeyboardNav onNavigateToEvents={mockNavigate} />);

      const event = new KeyboardEvent('keydown', { altKey: true, key: 'e' });
      window.dispatchEvent(event);

      expect(mockNavigate).toHaveBeenCalledTimes(1);
    });

    it('should call onNavigateToDetections when Alt+D is pressed', () => {
      const mockNavigate = jest.fn();
      render(<DashboardKeyboardNav onNavigateToDetections={mockNavigate} />);

      const event = new KeyboardEvent('keydown', { altKey: true, key: 'd' });
      window.dispatchEvent(event);

      expect(mockNavigate).toHaveBeenCalledTimes(1);
    });

    it('should call onNavigateToHealth when Alt+H is pressed', () => {
      const mockNavigate = jest.fn();
      render(<DashboardKeyboardNav onNavigateToHealth={mockNavigate} />);

      const event = new KeyboardEvent('keydown', { altKey: true, key: 'h' });
      window.dispatchEvent(event);

      expect(mockNavigate).toHaveBeenCalledTimes(1);
    });

    it('should clean up event listeners on unmount', () => {
      const mockRefresh = jest.fn();
      const { unmount } = render(<DashboardKeyboardNav onRefresh={mockRefresh} />);

      unmount();

      const event = new KeyboardEvent('keydown', { ctrlKey: true, key: 'r' });
      window.dispatchEvent(event);

      expect(mockRefresh).not.toHaveBeenCalled();
    });
  });
});