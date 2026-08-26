import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export default function DetectionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Detection Rules</h1>
        <p className="text-gray-600 mt-1">Manage detection rules and patterns</p>
      </div>

      <Card title="Detection Rules" subtitle="Configure detection patterns">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    </div>
  );
}