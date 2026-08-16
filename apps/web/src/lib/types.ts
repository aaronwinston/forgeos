export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
}

export interface Folder {
  id: number;
  project_id: number;
  parent_folder_id?: number;
  name: string;
  created_at: string;
}

export interface Deliverable {
  id: number;
  folder_id: number;
  content_type: string;
  title: string;
  status: string;
  body_md?: string;
  created_at: string;
  updated_at: string;
}

export interface Brief {
  id: number;
  project_id: number;
  deliverable_id?: number;
  brief_md: string;
  toggles_json?: string;
  created_at: string;
}

export interface ScrapeItem {
  id: number;
  source: string;
  source_url: string;
  title: string;
  body?: string;
  author?: string;
  published_at?: string;
  score_relevance?: number;
  score_reasoning?: string;
  dismissed_at?: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Toggles {
  brief_first: boolean;
  audience: string;
  voice: 'opinionated' | 'thoughtful' | 'objective' | 'technical' | 'founder';
  skills: string[] | 'auto';
  playbook: string | 'auto';
  content_type: string;
}

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

export interface TrendsData {
  id: number;
  keyword: string;
  region: string;
  interest_over_time_json?: string;
  related_queries_json?: string;
  fetched_at: string;
}

export interface GscQuery {
  id: number;
  query: string;
  impressions: number;
  clicks: number;
  ctr: number;
  position: number;
}

export interface KeywordCluster {
  id: number;
  keyword: string;
  region: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SeoRecommendation {
  recommendation_id: string;
  insight_id: number;
  topic: string;
  trends_momentum: 'rising' | 'steady' | 'falling' | 'no_data';
  recommendation_type: string;
  serp_gap_summary: string;
  recommended_action: string;
  priority_score: number;
  matched_keyword_cluster_id?: number;
  matched_keyword?: string;
  intent: {
    intent_stage: string;
    target_page_type: string;
    cta_suggestion: string;
  };
  movement: {
    baseline_position?: number;
    current_position?: number;
    position_delta?: number;
    baseline_clicks?: number;
    current_clicks?: number;
    click_delta?: number;
  };
}

export const CONTENT_TYPES = [
  'blog', 'email', 'press_release', 'analyst_briefing',
  'social_post', 'case_study', 'launch_copy', 'lifecycle_email',
  'newsletter', 'thought_leadership', 'other'
] as const;
