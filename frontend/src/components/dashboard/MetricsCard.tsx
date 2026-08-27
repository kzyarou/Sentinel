import { Card } from '@/components/common/Card';

interface MetricsCardProps {
  title: string;
  subtitle: string;
  value: number;
  color: string;
  icon?: string;
  ariaLabel?: string;
}

export function MetricsCard({
  title,
  subtitle,
  value,
  color,
  icon,
  ariaLabel
}: MetricsCardProps) {
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="flex items-center justify-between">
        <div className={`text-4xl font-bold ${color}`} aria-label={ariaLabel}>
          {value}
        </div>
        {icon && (
          <div className="text-2xl" aria-hidden="true">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}