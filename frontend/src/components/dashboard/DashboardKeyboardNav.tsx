import { useEffect } from 'react';

interface DashboardKeyboardNavProps {
  onRefresh?: () => void;
  onNavigateToFindings?: () => void;
  onNavigateToEvents?: () => void;
  onNavigateToDetections?: () => void;
  onNavigateToHealth?: () => void;
}

export function DashboardKeyboardNav({
  onRefresh,
  onNavigateToFindings,
  onNavigateToEvents,
  onNavigateToDetections,
  onNavigateToHealth
}: DashboardKeyboardNavProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + R for refresh
      if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        onRefresh?.();
      }

      // Alt + F for findings
      if (e.altKey && e.key === 'f') {
        e.preventDefault();
        onNavigateToFindings?.();
      }

      // Alt + E for events
      if (e.altKey && e.key === 'e') {
        e.preventDefault();
        onNavigateToEvents?.();
      }

      // Alt + D for detections
      if (e.altKey && e.key === 'd') {
        e.preventDefault();
        onNavigateToDetections?.();
      }

      // Alt + H for health
      if (e.altKey && e.key === 'h') {
        e.preventDefault();
        onNavigateToHealth?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onRefresh, onNavigateToFindings, onNavigateToEvents, onNavigateToDetections, onNavigateToHealth]);

  return null; // This component doesn't render anything
}