import { validateConfig } from './config';

// Validate configuration on module load
if (typeof window !== 'undefined') {
  try {
    validateConfig();
  } catch (error) {
    console.error('Configuration validation failed:', error);
    // In development, we'll log but not crash - fallback to localhost:8000
    // In production, this should fail hard
    if (process.env.NODE_ENV === 'production') {
      throw error;
    }
  }
}

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export function getApiBase(): string {
  return API_BASE;
}

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
  error?: 'API_UNREACHABLE' | 'API_HTTP_ERROR' | 'API_PARSE_ERROR';
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
  error: 'API_UNREACHABLE' | 'API_HTTP_ERROR' | 'API_PARSE_ERROR';
  status?: number;
  details?: string;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T | ApiError> {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options?.headers as Record<string, string>,
    };
    
    const res = await fetch(`${API_BASE}${path}`, {
      credentials: 'include', // Always send cookies for auth
      headers,
      ...options,
    });
    if (!res.ok) {
      const details = await res.text().catch(() => undefined);
      console.error(`API error ${res.status} for ${path}:`, details);
      return { 
        error: 'API_HTTP_ERROR', 
        status: res.status, 
        details: details || undefined 
      };
    }
    return res.json();
  } catch (err) {
    console.error(`API unreachable for ${path}:`, err);
    return { 
      error: 'API_UNREACHABLE', 
      details: err instanceof Error ? err.message : 'Unknown error' 
    };
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
  if (isApiError(result)) return { stories: [], refreshed_at: null, error: result.error };
  return result;
}

export async function getBriefingByDate(date: string): Promise<BriefingResponse> {
  const result = await apiFetch<BriefingResponse>(`/api/briefing?date=${encodeURIComponent(date)}`);
  if (isApiError(result)) return { stories: [], refreshed_at: null, error: result.error };
  return result;
}

export async function refreshBriefing(): Promise<BriefingResponse> {
  const result = await apiFetch<BriefingResponse>('/api/briefing/refresh', { method: 'POST' });
  if (isApiError(result)) return { stories: [], refreshed_at: null, error: result.error };
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
  scrapeItemIds?: number[],
): () => void {
  const controller = new AbortController();
  
  fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      scrape_item_ids: scrapeItemIds ?? [],
    }),
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

// ---------------------------------------------------------------------------
// Calendar types
// ---------------------------------------------------------------------------

export type ContentType = 'blog' | 'email' | 'press-release' | 'case-study' | 'whitepaper' | 'launch';
export type CalendarEventStatus = 'pending' | 'confirmed' | 'cancelled';
export type SyncStatus = 'synced' | 'syncing' | 'offline';

export interface CalendarEvent {
  id: number;
  deliverable_id: number | null;
  project_id: number | null;
  google_event_id: string | null;
  title: string;
  content_type: ContentType;
  description: string | null;
  notes: string | null;
  start_at: string;  // ISO 8601
  end_at: string | null;
  all_day: boolean;
  status: CalendarEventStatus;
  sync_status: SyncStatus;
  last_synced_at: string | null;
  synced_to_google_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CalendarEventCreatePayload {
  title: string;
  content_type: ContentType;
  start_at: string;
  end_at?: string;
  all_day?: boolean;
  status?: CalendarEventStatus;
  notes?: string;
  deliverable_id?: number;
  project_id?: number;
  folder_id?: number;
}

export interface CalendarEventPatchPayload {
  title?: string;
  content_type?: ContentType;
  start_at?: string;
  end_at?: string;
  all_day?: boolean;
  status?: CalendarEventStatus;
  sync_status?: SyncStatus;
  google_event_id?: string;
  notes?: string;
  deliverable_id?: number;
}

export interface CalendarEventCreateResponse extends CalendarEvent {
  deliverable?: { id: number; title: string };
}

// ---------------------------------------------------------------------------
// Calendar API functions
// ---------------------------------------------------------------------------

export async function getCalendarEvents(start?: string, end?: string): Promise<CalendarEvent[]> {
  const params = new URLSearchParams();
  if (start) params.set('start', start);
  if (end) params.set('end', end);
  const qs = params.toString();
  const result = await apiFetch<CalendarEvent[]>(`/api/calendar/events${qs ? `?${qs}` : ''}`);
  if (isApiError(result)) return [];
  return result;
}

export async function getUpcomingEvents(limit = 5): Promise<CalendarEvent[]> {
  const result = await apiFetch<CalendarEvent[]>(`/api/calendar/events/upcoming?limit=${limit}`);
  if (isApiError(result)) return [];
  return result;
}

export async function createCalendarEvent(
  data: CalendarEventCreatePayload,
): Promise<CalendarEventCreateResponse | ApiError> {
  return apiFetch<CalendarEventCreateResponse>('/api/calendar/events', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCalendarEvent(
  id: number,
  data: CalendarEventPatchPayload,
): Promise<CalendarEvent | ApiError> {
  return apiFetch<CalendarEvent>(`/api/calendar/events/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteCalendarEvent(id: number): Promise<void> {
  await apiFetch(`/api/calendar/events/${id}`, { method: 'DELETE' });
}

export interface Folder {
  id: number;
  name: string;
  parent_folder_id: number | null;
}

/** Fetch folders for a project — used by NewEventModal folder picker */
export async function getProjectFolders(projectId: number): Promise<Folder[]> {
  const result = await apiFetch<Folder[]>(`/api/calendar/projects/${projectId}/folders`);
  if (isApiError(result)) return [];
  return result;
}

// Search Intelligence API

export interface SearchInsight {
  id: number;
  topic: string;
  source_item_ids: string;
  our_gsc_position?: number;
  our_gsc_clicks?: number;
  trends_momentum: 'rising' | 'steady' | 'falling' | 'no_data';
  insight_text: string;
  generated_at: string;
}

export interface KeywordCluster {
  id: number;
  keyword: string;
  region: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export async function getSearchInsights(): Promise<SearchInsight[]> {
  const result = await apiFetch<SearchInsight[]>('/api/intelligence/search/insights');
  if (isApiError(result)) return [];
  return result;
}

export async function getKeywordClusters(): Promise<KeywordCluster[]> {
  const result = await apiFetch<KeywordCluster[]>('/api/intelligence/search/keywords');
  if (isApiError(result)) return [];
  return result;
}

export async function addKeywordCluster(keyword: string, region: string = 'US'): Promise<KeywordCluster | ApiError> {
  return apiFetch<KeywordCluster>('/api/intelligence/search/keywords', {
    method: 'POST',
    body: JSON.stringify({ keyword, region }),
  });
}

export async function updateKeywordCluster(
  clusterId: number,
  data: { active?: boolean; keyword?: string },
): Promise<KeywordCluster | ApiError> {
  return apiFetch<KeywordCluster>(`/api/intelligence/search/keywords/${clusterId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteKeywordCluster(clusterId: number): Promise<void> {
  await apiFetch(`/api/intelligence/search/keywords/${clusterId}`, { method: 'DELETE' });
}
