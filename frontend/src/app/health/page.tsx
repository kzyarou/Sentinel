import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export default function HealthPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
        <p className="text-gray-600 mt-1">System status and monitoring</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Backend Status" subtitle="API service health">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
        <Card title="Database Status" subtitle="Database connectivity">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        </Card>
      </div>

      <Card title="System Metrics" subtitle="Performance and resource usage">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    </div>
  );
}