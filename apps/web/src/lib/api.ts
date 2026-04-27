const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Session {
  id: number;
  brief_id: number;
  deliverable_id?: number;
  title: string;
  type: string;
  audience?: string;
  description?: string;
  status: 'pending' | 'active' | 'complete';
  current_agent?: string;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface Story {
  id: string;
  title: string;
  source: 'HackerNews' | 'GitHub' | 'ArXiv';
  sourceColor: string;
  icon: string;
  why_relevant: string;
  engagement_signal: string;
  content_angle: string;
  url: string;
  trending: boolean;
}

export interface BriefingResponse {
  stories: Story[];
  refreshed_at: number | null;
  error?: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
}

export interface Deliverable {
  id: number;
  folder_id: number;
  content_type: string;
  title: string;
  status: 'draft' | 'active' | 'published';
  body_md?: string;
  metadata_json?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  error: 'API_UNAVAILABLE';
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T | ApiError> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      console.error(`API error ${res.status} for ${path}`);
      return { error: 'API_UNAVAILABLE' };
    }
    return res.json();
  } catch {
    return { error: 'API_UNAVAILABLE' };
  }
}

export function isApiError(val: unknown): val is ApiError {
  return typeof val === 'object' && val !== null && 'error' in val;
}

export async function checkHealth(): Promise<{ ok: boolean; reason?: string }> {
  try {
    const resp = await fetch(`${API_BASE}/api/health`, { method: 'GET' });
    return { ok: resp.ok };
  } catch {
    return { ok: false, reason: 'api-unreachable' };
  }
}

export async function getSessions(): Promise<Session[]> {
  const result = await apiFetch<Session[]>('/api/sessions');
  if (isApiError(result)) return [];
  return result;
}

export async function createSession(data: { title: string; type: string; audience?: string; description?: string }): Promise<Session | ApiError> {
  return apiFetch<Session>('/api/sessions', { method: 'POST', body: JSON.stringify(data) });
}

export async function getSessionById(id: number): Promise<Session | ApiError> {
  return apiFetch<Session>(`/api/sessions/${id}`);
}

export async function getDeliverableById(id: number): Promise<Deliverable | ApiError> {
  return apiFetch<Deliverable>(`/api/deliverables/${id}`);
}

export async function updateSession(id: number, data: Partial<Session>): Promise<Session | ApiError> {
  return apiFetch<Session>(`/api/sessions/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteSession(id: number): Promise<void> {
  await apiFetch(`/api/sessions/${id}`, { method: 'DELETE' });
}

export async function runSession(id: number): Promise<void> {
  await apiFetch(`/api/sessions/${id}/run`, { method: 'POST' });
}

export async function getBriefing(): Promise<BriefingResponse> {
  const result = await apiFetch<BriefingResponse>('/api/briefing');
  if (isApiError(result)) return { stories: [], refreshed_at: null, error: 'API_UNAVAILABLE' };
  return result;
}

export async function refreshBriefing(): Promise<BriefingResponse> {
  const result = await apiFetch<BriefingResponse>('/api/briefing/refresh', { method: 'POST' });
  if (isApiError(result)) return { stories: [], refreshed_at: null, error: 'API_UNAVAILABLE' };
  return result;
}

export async function getProjects(): Promise<Project[]> {
  const result = await apiFetch<Project[]>('/api/projects');
  if (isApiError(result)) return [];
  return result;
}

export function streamSession(
  sessionId: number,
  onUpdate: (event: Record<string, unknown>) => void,
): () => void {
  const es = new EventSource(`${API_BASE}/api/sessions/${sessionId}/stream`);
  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onUpdate(data);
      if (data.type === 'done') es.close();
    } catch {}
  };
  es.onerror = () => es.close();
  return () => es.close();
}

export function streamChat(
  message: string,
  sessionId: number | undefined,
  onChunk: (chunk: string) => void,
  onComplete?: () => void,
  onError?: (error: string) => void,
): () => void {
  const controller = new AbortController();
  
  fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal: controller.signal,
  }).then(async (res) => {
    if (!res.ok) {
      onError?.(`Failed to send message: ${res.status}`);
      return;
    }
    const reader = res.body?.getReader();
    if (!reader) {
      onError?.('No response body');
      return;
    }
    const decoder = new TextDecoder();
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          onComplete?.();
          break;
        }
        const text = decoder.decode(value);
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) onChunk(data.chunk);
            } catch {}
          }
        }
      }
    } catch (e) {
      onError?.(e instanceof Error ? e.message : 'Unknown error');
    }
  }).catch((e) => {
    onError?.(e instanceof Error ? e.message : 'Network error');
  });
  
  return () => controller.abort();
}

export const api = {
  getProjects: () => getProjects(),
  createProject: (data: { name: string; description?: string }) =>
    apiFetch<Project>('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
  deleteProject: (id: number) => apiFetch<unknown>(`/api/projects/${id}`, { method: 'DELETE' }),
  getFolders: (projectId: number) => apiFetch<unknown[]>(`/api/projects/${projectId}/folders`),
  createFolder: (data: unknown) => apiFetch<unknown>('/api/folders', { method: 'POST', body: JSON.stringify(data) }),
  deleteFolder: (id: number) => apiFetch<unknown>(`/api/folders/${id}`, { method: 'DELETE' }),
  getDeliverables: (folderId: number) => apiFetch<unknown[]>(`/api/folders/${folderId}/deliverables`),
  createDeliverable: (data: unknown) => apiFetch<unknown>('/api/deliverables', { method: 'POST', body: JSON.stringify(data) }),
  updateDeliverable: (id: number, data: unknown) => apiFetch<unknown>(`/api/deliverables/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteDeliverable: (id: number) => apiFetch<unknown>(`/api/deliverables/${id}`, { method: 'DELETE' }),
  getFeed: () => apiFetch<unknown[]>('/api/intelligence/feed'),
  getItems: () => apiFetch<unknown[]>('/api/intelligence/items'),
  dismissItem: (id: number) => apiFetch<unknown>(`/api/intelligence/items/${id}/dismiss`, { method: 'POST' }),
  useAsContext: (id: number) => apiFetch<unknown>(`/api/intelligence/items/${id}/use-as-context`, { method: 'POST' }),
  triggerScrape: () => apiFetch<unknown>('/api/intelligence/scrape', { method: 'POST' }),
  getFileTree: () => apiFetch<unknown>('/api/files/tree'),
  getSkills: () => apiFetch<unknown[]>('/api/files/skills'),
  getPlaybooks: () => apiFetch<unknown[]>('/api/files/playbooks'),
  readFile: (path: string) => apiFetch<unknown>(`/api/files/read?path=${encodeURIComponent(path)}`),
  writeFile: (path: string, content: string) => apiFetch<unknown>('/api/files/write', { method: 'POST', body: JSON.stringify({ path, content }) }),
  createChatSession: (projectId?: number) => apiFetch<unknown>('/api/chat/session', { method: 'POST', body: JSON.stringify({ project_id: projectId }) }),
  getMessages: (sessionId: number) => apiFetch<unknown[]>(`/api/chat/session/${sessionId}/messages`),
  generateBrief: (data: unknown) => apiFetch<unknown>('/api/chat/brief', { method: 'POST', body: JSON.stringify(data) }),
};
