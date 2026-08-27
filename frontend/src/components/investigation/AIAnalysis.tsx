import { Card } from '@/components/common/Card';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { AIAnalysis } from '@/types';
import { safeText, truncateText } from '@/lib/safe-rendering';

interface AIAnalysisProps {
  aiAnalysis: AIAnalysis | null;
  loading?: boolean;
  error?: string | null;
  onRequestAnalysis?: () => void;
  canRequestAnalysis?: boolean;
}

export function AIAnalysis({ 
  aiAnalysis, 
  loading = false, 
  error = null, 
  onRequestAnalysis,
  canRequestAnalysis = false 
}: AIAnalysisProps) {
  if (loading) {
    return (
      <Card title="AI-Assisted Analysis" subtitle="AI-generated investigation insights">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
          <span className="ml-3 text-gray-600">Processing AI analysis...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="AI-Assisted Analysis" subtitle="AI-generated investigation insights">
        <Alert type="error" message={error} />
        {canRequestAnalysis && onRequestAnalysis && (
          <div className="mt-4">
            <Button onClick={onRequestAnalysis} variant="secondary" size="sm">
              Retry Analysis
            </Button>
          </div>
        )}
      </Card>
    );
  }

  if (!aiAnalysis) {
    return (
      <Card title="AI-Assisted Analysis" subtitle="AI-generated investigation insights">
        <div className="space-y-4">
          {/* Advisory Notice */}
          <div className="p-3 bg-amber-50 border border-amber-200 rounded">
            <div className="flex items-start gap-2">
              <span className="text-amber-500 text-lg" aria-hidden="true">⚠️</span>
              <div>
                <h4 className="text-sm font-medium text-amber-900 mb-1">AI-Generated Content</h4>
                <p className="text-xs text-amber-800">
                  AI analysis is advisory and should not be treated as authoritative security evidence.
                  Always verify AI suggestions with manual investigation.
                </p>
              </div>
            </div>
          </div>

          {/* No Analysis State */}
          <div className="text-center py-8 text-gray-500">
            <p className="mb-4">No AI analysis has been generated yet.</p>
            <p className="text-sm text-gray-400 mb-4">
              Request AI analysis to get contextual insights and investigation suggestions.
            </p>
            {canRequestAnalysis && onRequestAnalysis && (
              <Button onClick={onRequestAnalysis} variant="primary">
                Analyze with AI
              </Button>
            )}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card title="AI-Assisted Analysis" subtitle="AI-generated investigation insights">
      <div className="space-y-4">
        {/* Advisory Notice */}
        <div className="p-3 bg-amber-50 border border-amber-200 rounded">
          <div className="flex items-start gap-2">
            <span className="text-amber-500 text-lg" aria-hidden="true">⚠️</span>
            <div>
              <h4 className="text-sm font-medium text-amber-900 mb-1">AI-Generated Content</h4>
              <p className="text-xs text-amber-800">
                This analysis is AI-generated and advisory. It should not be treated as authoritative 
                security evidence. Always verify AI suggestions with manual investigation.
              </p>
            </div>
          </div>
        </div>

        {/* Analysis Metadata */}
        <div className="flex justify-between items-center text-xs text-gray-600">
          <div>
            <span className="font-medium">Generated:</span>{' '}
            <time dateTime={aiAnalysis.created_at}>
              {new Date(aiAnalysis.created_at).toLocaleString()}
            </time>
          </div>
          {aiAnalysis.model_used && (
            <div>
              <span className="font-medium">Model:</span> {safeText(aiAnalysis.model_used)}
            </div>
          )}
        </div>

        {/* Summary */}
        {aiAnalysis.summary && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Summary</h4>
            <div className="p-3 bg-gray-50 border border-gray-200 rounded">
              <p className="text-sm text-gray-700">
                {truncateText(aiAnalysis.summary, 500)}
              </p>
            </div>
          </div>
        )}

        {/* Main Analysis (fallback if no summary) */}
        {!aiAnalysis.summary && aiAnalysis.analysis && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis</h4>
            <div className="p-3 bg-gray-50 border border-gray-200 rounded">
              <p className="text-sm text-gray-700">
                {truncateText(aiAnalysis.analysis, 500)}
              </p>
            </div>
          </div>
        )}

        {/* Observed Indicators */}
        {aiAnalysis.indicators && aiAnalysis.indicators.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Observed Indicators</h4>
            <ul className="list-disc list-inside space-y-1">
              {aiAnalysis.indicators.map((indicator, index) => (
                <li key={index} className="text-sm text-gray-600">
                  {safeText(indicator)}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Possible Interpretation */}
        {aiAnalysis.interpretation && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Possible Interpretation</h4>
            <div className="p-3 bg-gray-50 border border-gray-200 rounded">
              <p className="text-sm text-gray-700">
                {truncateText(aiAnalysis.interpretation, 500)}
              </p>
            </div>
          </div>
        )}

        {/* Investigation Suggestions */}
        {(aiAnalysis.suggestions && aiAnalysis.suggestions.length > 0) || (aiAnalysis.recommendations && aiAnalysis.recommendations.length > 0) ? (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Investigation Suggestions</h4>
            <ul className="list-disc list-inside space-y-1">
              {(aiAnalysis.suggestions || aiAnalysis.recommendations || []).map((suggestion, index) => (
                <li key={index} className="text-sm text-gray-600">
                  {safeText(suggestion)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {/* Uncertainty Notes */}
        {aiAnalysis.uncertainty_notes && aiAnalysis.uncertainty_notes.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Uncertainty Notes</h4>
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
              <ul className="list-disc list-inside space-y-1">
                {aiAnalysis.uncertainty_notes.map((note, index) => (
                  <li key={index} className="text-sm text-yellow-800">
                    {safeText(note)}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Confidence Score */}
        {aiAnalysis.confidence !== undefined && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Analysis Confidence</h4>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${aiAnalysis.confidence * 100}%` }}
                  role="progressbar"
                  aria-valuenow={aiAnalysis.confidence * 100}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
              <span className="text-sm text-gray-600">
                {Math.round(aiAnalysis.confidence * 100)}%
              </span>
            </div>
          </div>
        )}

        {/* Refresh/Request New Analysis */}
        {canRequestAnalysis && onRequestAnalysis && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Button onClick={onRequestAnalysis} variant="secondary" size="sm">
              Request New Analysis
            </Button>
          </div>
        )}

        {/* Visual Distinction Label */}
        <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded">
          <p className="text-xs text-purple-800">
            <strong>Content Type:</strong> AI-Assisted Analysis (Advisory) vs. Authoritative Evidence
          </p>
        </div>
      </div>
    </Card>
  );
}