'use client';

import { useCallback, useState } from 'react';

export interface UseMutationOptions<T, E = Error> {
  onSuccess?: (data: T) => void;
  onError?: (error: E) => void;
  onSettled?: () => void;
}

export interface UseMutationResult<T, E = Error> {
  mutate: (data: unknown) => Promise<T | undefined>;
  mutateAsync: (data: unknown) => Promise<T>;
  isLoading: boolean;
  error: E | null;
  data: T | null;
  reset: () => void;
}

export function useMutation<T, E = Error>(
  mutationFn: (data: unknown) => Promise<T>,
  options?: UseMutationOptions<T, E>
): UseMutationResult<T, E> {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<E | null>(null);
  const [data, setData] = useState<T | null>(null);

  const mutateAsync = useCallback(async (payload: unknown): Promise<T> => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await mutationFn(payload);
      setData(result);
      options?.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err as E;
      setError(error);
      options?.onError?.(error);
      throw err;
    } finally {
      setIsLoading(false);
      options?.onSettled?.();
    }
  }, [mutationFn, options]);

  const mutate = useCallback(async (payload: unknown) => {
    try {
      return await mutateAsync(payload);
    } catch {
      return undefined;
    }
  }, [mutateAsync]);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setData(null);
  }, []);

  return { mutate, mutateAsync, isLoading, error, data, reset };
}
