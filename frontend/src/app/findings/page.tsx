import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export default function FindingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Findings</h1>
        <p className="text-gray-600 mt-1">Security findings and investigations</p>
      </div>

      <Card title="Security Findings" subtitle="View and manage security findings">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    </div>
  );
}