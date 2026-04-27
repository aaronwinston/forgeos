'use client';

import { useCallback, useState } from 'react';

export interface UseFormOptions<T> {
  onSubmit: (data: T) => Promise<void>;
  onSuccess?: (data?: T) => void;
  onError?: (error: Error) => void;
}

export interface UseFormResult<T> {
  isSubmitting: boolean;
  error: Error | null;
  submit: (data: T) => Promise<void>;
  clearError: () => void;
}

export function useForm<T>({
  onSubmit,
  onSuccess,
  onError,
}: UseFormOptions<T>): UseFormResult<T> {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const submit = useCallback(async (data: T) => {
    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(data);
      onSuccess?.(data);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onError?.(error);
    } finally {
      setIsSubmitting(false);
    }
  }, [onSubmit, onSuccess, onError]);

  const clearError = useCallback(() => setError(null), []);

  return { isSubmitting, error, submit, clearError };
}
