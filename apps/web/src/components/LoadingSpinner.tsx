'use client';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary';
  className?: string;
}

export function LoadingSpinner({
  size = 'md',
  color = 'primary',
  className = '',
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  const colorClasses = {
    primary: 'text-accent',
    secondary: 'text-fg-secondary',
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <svg
        className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-label="Loading"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}

interface SkeletonLoaderProps {
  count?: number;
  variant?: 'card' | 'text' | 'avatar';
  className?: string;
}

export function SkeletonLoader({
  count = 1,
  variant = 'card',
  className = '',
}: SkeletonLoaderProps) {
  if (variant === 'card') {
    return (
      <div className={`space-y-4 ${className}`}>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="border border-border rounded-card p-4 bg-bg-secondary overflow-hidden">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-4 w-16 rounded-chip bg-bg-tertiary animate-shimmer" />
              <div className="h-3 w-8 rounded-chip bg-bg-tertiary animate-shimmer" />
            </div>
            <div className="space-y-2 mb-3">
              <div className="h-4 w-full rounded-chip bg-bg-tertiary animate-shimmer" />
              <div className="h-4 w-3/4 rounded-chip bg-bg-tertiary animate-shimmer" />
            </div>
            <div className="h-3 w-full rounded-chip bg-bg-tertiary animate-shimmer mb-2" />
            <div className="h-3 w-2/3 rounded-chip bg-bg-tertiary animate-shimmer" />
          </div>
        ))}
      </div>
    );
  }

  if (variant === 'text') {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="h-4 w-full rounded-chip bg-bg-tertiary animate-shimmer" />
        ))}
      </div>
    );
  }

  if (variant === 'avatar') {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="w-10 h-10 rounded-full bg-bg-tertiary animate-shimmer" />
        <div className="flex-1 space-y-2">
          <div className="h-4 w-1/2 rounded-chip bg-bg-tertiary animate-shimmer" />
          <div className="h-3 w-1/3 rounded-chip bg-bg-tertiary animate-shimmer" />
        </div>
      </div>
    );
  }

  return null;
}

interface LoadingOverlayProps {
  isLoading: boolean;
  children: React.ReactNode;
  message?: string;
}

export function LoadingOverlay({
  isLoading,
  children,
  message = 'Loading...',
}: LoadingOverlayProps) {
  return (
    <div className="relative">
      {children}
      {isLoading && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-card">
          <div className="flex flex-col items-center gap-3">
            <LoadingSpinner size="lg" />
            <p className="text-sm text-fg-secondary">{message}</p>
          </div>
        </div>
      )}
    </div>
  );
}
