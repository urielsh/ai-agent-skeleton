/** API response types */

export interface DependencyHealth {
  status: string;
  latency_ms?: number;
}

export interface HealthResponse {
  status: string;
  database: DependencyHealth;
  redis: DependencyHealth;
}

export interface SessionResponse {
  session_id: string;
  status: string;
  draft_input: Record<string, unknown> | null;
  created_at?: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  draft_input: Record<string, unknown> | null;
  missing_fields: string[];
  next_questions: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface MessageHistoryResponse {
  messages: ChatMessage[];
}

export interface ComputeResponse {
  session_id: string;
  score: number;
  label: string;
  summary: string;
  breakdown: Record<string, unknown>;
  cached: boolean;
}

export interface ErrorResponse {
  detail: string;
}
