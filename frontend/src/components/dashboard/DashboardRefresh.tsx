import { Button } from '@/components/common/Button';
import { useState } from 'react';

interface DashboardRefreshProps {
  onRefresh: () => void;
  isLoading?: boolean;
  lastRefresh?: Date | null;
  autoRefresh?: boolean;
  onToggleAutoRefresh?: () => void;
}

export function DashboardRefresh({
  onRefresh,
  isLoading = false,
  lastRefresh = null,
  autoRefresh = false,
  onToggleAutoRefresh
}: DashboardRefreshProps) {
  const [buttonFocused, setButtonFocused] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onRefresh();
    }
  };

  return (
    <div className="flex items-center gap-4">
      {lastRefresh && (
        <div className="text-sm text-gray-600" aria-live="polite">
          Last updated: {lastRefresh.toLocaleTimeString()}
        </div>
      )}
      <Button
        onClick={onRefresh}
        disabled={isLoading}
        variant="secondary"
        size="sm"
        aria-label="Refresh dashboard data"
        aria-busy={isLoading}
        onKeyDown={handleKeyDown}
        onFocus={() => setButtonFocused(true)}
        onBlur={() => setButtonFocused(false)}
        className={buttonFocused ? 'ring-2 ring-blue-500' : ''}
      >
        {isLoading ? 'Refreshing...' : 'Refresh'}
      </Button>
      {onToggleAutoRefresh && (
        <button
          onClick={onToggleAutoRefresh}
          disabled={isLoading}
          className={`px-3 py-1.5 text-sm rounded border ${
            autoRefresh
              ? 'bg-blue-50 border-blue-300 text-blue-700'
              : 'bg-gray-50 border-gray-300 text-gray-700'
          } disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500`}
          aria-label={autoRefresh ? 'Disable auto refresh' : 'Enable auto refresh'}
          aria-pressed={autoRefresh}
        >
          Auto-refresh: {autoRefresh ? 'On' : 'Off'}
        </button>
      )}
    </div>
  );
}