'use client';

import { useEffect, useState } from 'react';

interface ProgressBarProps {
  isLoading: boolean;
  color?: 'primary' | 'success' | 'warning' | 'error';
}

export function ProgressBar({ isLoading, color = 'primary' }: ProgressBarProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setProgress(100);
      const timer = setTimeout(() => setProgress(0), 500);
      return () => clearTimeout(timer);
    }

    setProgress(10);

    const intervals = [
      setTimeout(() => setProgress(20), 100),
      setTimeout(() => setProgress(40), 300),
      setTimeout(() => setProgress(60), 800),
      setTimeout(() => setProgress(80), 1200),
    ];

    return () => {
      intervals.forEach((timer) => clearTimeout(timer));
    };
  }, [isLoading]);

  const colorClasses = {
    primary: 'bg-accent',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
  };

  return (
    <div className="fixed top-0 left-0 right-0 h-1 bg-transparent z-50">
      <div
        className={`h-full ${colorClasses[color]} transition-all duration-300 ease-out`}
        style={{ width: `${progress}%` }}
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
      />
    </div>
  );
}
