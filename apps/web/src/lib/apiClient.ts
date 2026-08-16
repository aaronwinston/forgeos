import { getApiBase } from './api';
import { getCSRFToken } from './csrf';

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase();
  const isWriteMethod = WRITE_METHODS.has(method);

  const baseHeaders: Record<string, string> = {};
  if (isWriteMethod) {
    if (options.body !== undefined) {
      baseHeaders['Content-Type'] = 'application/json';
    }
    if (typeof window !== 'undefined') {
      baseHeaders['X-CSRF-Token'] = getCSRFToken();
    }
  }

  const res = await fetch(`${getApiBase()}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      ...baseHeaders,
      ...(options.headers as Record<string, string> | undefined),
    },
  });

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/signin';
    }
    throw new ApiError(401, null, 'Unauthorized');
  }

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text().catch(() => null);
    }
    const message =
      typeof body === 'object' &&
      body !== null &&
      'message' in body &&
      typeof (body as { message: unknown }).message === 'string'
        ? (body as { message: string }).message
        : `HTTP ${res.status}`;
    throw new ApiError(res.status, body, message);
  }

  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return undefined as unknown as T;
  }

  return res.json() as Promise<T>;
}

export const apiGet = <T>(path: string, options?: RequestInit): Promise<T> =>
  apiFetch<T>(path, { ...options, method: 'GET' });

export const apiPost = <T>(
  path: string,
  body?: unknown,
  options?: RequestInit,
): Promise<T> =>
  apiFetch<T>(path, {
    ...options,
    method: 'POST',
    body: body !== undefined ? JSON.stringify(body) : undefined,
    headers: { ...(options?.headers as Record<string, string> | undefined) },
  });

export const apiPut = <T>(
  path: string,
  body?: unknown,
  options?: RequestInit,
): Promise<T> =>
  apiFetch<T>(path, {
    ...options,
    method: 'PUT',
    body: body !== undefined ? JSON.stringify(body) : undefined,
    headers: { ...(options?.headers as Record<string, string> | undefined) },
  });

export const apiDelete = <T = void>(
  path: string,
  options?: RequestInit,
): Promise<T> => apiFetch<T>(path, { ...options, method: 'DELETE' });
