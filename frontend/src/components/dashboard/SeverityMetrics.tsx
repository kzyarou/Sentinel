import { MetricsCard } from './MetricsCard';

interface SeverityMetricsProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
  loading?: boolean;
}

export function SeverityMetrics({
  critical,
  high,
  medium,
  low,
  total,
  loading = false
}: SeverityMetricsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-gray-100 rounded-lg animate-pulse" aria-label="Loading metrics" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricsCard
        title="Critical"
        subtitle="Critical severity findings"
        value={critical}
        color="text-red-600"
        icon="🔴"
        ariaLabel={`${critical} critical findings`}
      />
      <MetricsCard
        title="High"
        subtitle="High severity findings"
        value={high}
        color="text-orange-600"
        icon="🟠"
        ariaLabel={`${high} high severity findings`}
      />
      <MetricsCard
        title="Medium"
        subtitle="Medium severity findings"
        value={medium}
        color="text-yellow-600"
        icon="🟡"
        ariaLabel={`${medium} medium severity findings`}
      />
      <MetricsCard
        title="Total"
        subtitle="Total open findings"
        value={total}
        color="text-blue-600"
        icon="📊"
        ariaLabel={`${total} total findings`}
      />
    </div>
  );
}