import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Security monitoring overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card title="Total Findings" subtitle="Security findings">
          <div className="text-4xl font-bold text-blue-600">0</div>
        </Card>
        <Card title="Critical" subtitle="High severity findings">
          <div className="text-4xl font-bold text-red-600">0</div>
        </Card>
        <Card title="Events Today" subtitle="Security events">
          <div className="text-4xl font-bold text-green-600">0</div>
        </Card>
        <Card title="Active Rules" subtitle="Detection rules">
          <div className="text-4xl font-bold text-purple-600">0</div>
        </Card>
      </div>

      <Card title="Recent Activity" subtitle="Latest security events">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    </div>
  );
}