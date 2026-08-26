import Link from 'next/link';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-gray-50">
      <main className="flex flex-1 w-full max-w-5xl flex-col items-center justify-center py-32 px-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Sentinel
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            AI-Assisted Cybersecurity Monitoring Platform
          </p>
          <p className="text-gray-500">
            Detect, analyze, and respond to security threats with AI-powered insights
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 w-full">
          <Card title="Event Ingestion" subtitle="Collect security telemetry">
            <p className="text-gray-600">
              Gather security events from multiple sources with normalized data processing
            </p>
          </Card>
          <Card title="Detection Engine" subtitle="Identify threats">
            <p className="text-gray-600">
              Apply deterministic detection rules to identify suspicious behavior patterns
            </p>
          </Card>
          <Card title="AI Analysis" subtitle="Get insights">
            <p className="text-gray-600">
              Leverage AI to provide contextual explanations and investigation guidance
            </p>
          </Card>
        </div>

        <div className="flex gap-4">
          <Link href="/login">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="secondary" size="lg">View Dashboard</Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
