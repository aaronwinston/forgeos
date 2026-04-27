'use client';

import { useCallback, useReducer } from 'react';

export interface UseAsyncState<T> {
  loading: boolean;
  error: Error | null;
  data: T | null;
}

export interface UseAsyncActions<T> {
  execute: <Args extends unknown[]>(promise: Promise<T>) => Promise<T>;
  reset: () => void;
  setData: (data: T) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: Error | null) => void;
}

type Action<T> = | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_DATA'; payload: T }
  | { type: 'SET_ERROR'; payload: Error }
  | { type: 'RESET' };

function asyncReducer<T>(state: UseAsyncState<T>, action: Action<T>): UseAsyncState<T> {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload, error: action.payload ? state.error : null };
    case 'SET_DATA':
      return { ...state, data: action.payload, loading: false, error: null };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'RESET':
      return { loading: false, error: null, data: null };
    default:
      return state;
  }
}

export function useAsync<T>(initialData?: T): UseAsyncState<T> & UseAsyncActions<T> {
  const [state, dispatch] = useReducer(asyncReducer<T>, {
    loading: false,
    error: null,
    data: initialData ?? null,
  });

  const execute = useCallback(async <Args extends unknown[]>(promise: Promise<T>): Promise<T> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const data = await promise;
      dispatch({ type: 'SET_DATA', payload: data });
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      dispatch({ type: 'SET_ERROR', payload: err });
      throw err;
    }
  }, []);

  const reset = useCallback(() => dispatch({ type: 'RESET' }), []);
  const setData = useCallback((data: T) => dispatch({ type: 'SET_DATA', payload: data }), []);
  const setLoading = useCallback((loading: boolean) => dispatch({ type: 'SET_LOADING', payload: loading }), []);
  const setError = useCallback((error: Error | null) => {
    if (error) {
      dispatch({ type: 'SET_ERROR', payload: error });
    } else {
      dispatch({ type: 'RESET' });
    }
  }, []);

  return { ...state, execute, reset, setData, setLoading, setError };
}
