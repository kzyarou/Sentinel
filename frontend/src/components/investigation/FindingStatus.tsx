import { useState } from 'react';
import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { Finding } from '@/types';
import { safeText } from '@/lib/safe-rendering';

interface FindingStatusProps {
  finding: Finding | null;
  onStatusChange: (newStatus: string) => void;
  loading?: boolean;
  error?: string | null;
}

// Valid status transitions based on finding lifecycle
const VALID_TRANSITIONS: Record<string, string[]> = {
  'OPEN': ['INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE'],
  'INVESTIGATING': ['OPEN', 'RESOLVED', 'FALSE_POSITIVE'],
  'RESOLVED': ['OPEN', 'INVESTIGATING'],
  'FALSE_POSITIVE': ['OPEN', 'INVESTIGATING']
};

const STATUS_LABELS: Record<string, string> = {
  'OPEN': 'Open',
  'INVESTIGATING': 'Investigating',
  'RESOLVED': 'Resolved',
  'FALSE_POSITIVE': 'False Positive'
};

const STATUS_DESCRIPTIONS: Record<string, string> = {
  'OPEN': 'Finding requires investigation',
  'INVESTIGATING': 'Finding is currently under investigation',
  'RESOLVED': 'Finding has been resolved',
  'FALSE_POSITIVE': 'Finding determined to be a false positive'
};

const STATUS_COLORS: Record<string, string> = {
  'OPEN': 'bg-red-100 text-red-800',
  'INVESTIGATING': 'bg-yellow-100 text-yellow-800',
  'RESOLVED': 'bg-green-100 text-green-800',
  'FALSE_POSITIVE': 'bg-gray-100 text-gray-800'
};

export function FindingStatus({ finding, onStatusChange, loading = false, error = null }: FindingStatusProps) {
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [showConfirmation, setShowConfirmation] = useState(false);

  if (loading) {
    return (
      <Card title="Finding Status" subtitle="Manage finding lifecycle">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Finding Status" subtitle="Manage finding lifecycle">
        <Alert type="error" message={error} />
      </Card>
    );
  }

  if (!finding) {
    return (
      <Card title="Finding Status" subtitle="Manage finding lifecycle">
        <div className="text-center py-8 text-gray-500">
          No finding data available
        </div>
      </Card>
    );
  }

  const currentStatus = finding.status;
  const validTransitions = VALID_TRANSITIONS[currentStatus] || [];

  const handleStatusSelect = (newStatus: string) => {
    setSelectedStatus(newStatus);
    setShowConfirmation(true);
  };

  const handleConfirmStatusChange = () => {
    if (selectedStatus) {
      onStatusChange(selectedStatus);
      setShowConfirmation(false);
      setSelectedStatus('');
    }
  };

  const handleCancelStatusChange = () => {
    setShowConfirmation(false);
    setSelectedStatus('');
  };

  return (
    <Card title="Finding Status" subtitle="Manage finding lifecycle">
      <div className="space-y-4">
        {/* Current Status Display */}
        <div className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Current Status</h4>
            <div className="flex items-center gap-2">
              <span 
                className={`px-3 py-1 rounded text-sm font-medium ${STATUS_COLORS[currentStatus]}`}
                aria-label={`Current status: ${STATUS_LABELS[currentStatus]}`}
              >
                {STATUS_LABELS[currentStatus]}
              </span>
              <span className="text-sm text-gray-600">
                {STATUS_DESCRIPTIONS[currentStatus]}
              </span>
            </div>
          </div>
        </div>

        {/* Status Change Options */}
        {validTransitions.length > 0 ? (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Change Status</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {validTransitions.map((status) => (
                <Button
                  key={status}
                  onClick={() => handleStatusSelect(status)}
                  variant="secondary"
                  size="sm"
                  disabled={showConfirmation}
                  aria-label={`Change status to ${STATUS_LABELS[status]}`}
                >
                  {STATUS_LABELS[status]}
                </Button>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500 text-sm">
            No valid status transitions available from current state
          </div>
        )}

        {/* Confirmation Dialog */}
        {showConfirmation && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
            <h4 className="text-sm font-medium text-yellow-900 mb-2">
              Confirm Status Change
            </h4>
            <p className="text-sm text-yellow-800 mb-3">
              Are you sure you want to change the status from{' '}
              <strong>{STATUS_LABELS[currentStatus]}</strong> to{' '}
              <strong>{STATUS_LABELS[selectedStatus]}</strong>?
            </p>
            <div className="flex gap-2">
              <Button 
                onClick={handleConfirmStatusChange} 
                variant="primary" 
                size="sm"
              >
                Confirm Change
              </Button>
              <Button 
                onClick={handleCancelStatusChange} 
                variant="secondary" 
                size="sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Authorization Notice */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-800">
            <strong>Authorization:</strong> Status changes are validated by the backend to ensure proper permissions.
            Invalid transitions will be rejected by the server.
          </p>
        </div>

        {/* Status Lifecycle Info */}
        <div className="p-3 bg-gray-50 border border-gray-200 rounded">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Status Lifecycle</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div><strong>Open:</strong> New finding requiring investigation</div>
            <div><strong>Investigating:</strong> Active investigation in progress</div>
            <div><strong>Resolved:</strong> Finding has been resolved</div>
            <div><strong>False Positive:</strong> Finding determined to be non-threatening</div>
          </div>
        </div>
      </div>
    </Card>
  );
}