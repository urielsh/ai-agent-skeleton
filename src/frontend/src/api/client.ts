/** HTTP client for the AI Agent Skeleton API. */

import type {
  ChatRequest,
  ChatResponse,
  ComputeResponse,
  HealthResponse,
  MessageHistoryResponse,
  SessionResponse,
} from "./types";

const API_BASE = "/api";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(
      body.detail || `Request failed: ${res.status}`,
      res.status,
      body
    );
  }

  return res.json() as Promise<T>;
}

// --- Health ---
export function getHealth(): Promise<HealthResponse> {
  return request("/health");
}

// --- Sessions ---
export function createSession(): Promise<SessionResponse> {
  return request("/sessions", { method: "POST" });
}

export function getSession(sessionId: string): Promise<SessionResponse> {
  return request(`/sessions/${sessionId}`);
}

export function deleteSession(sessionId: string): Promise<SessionResponse> {
  return request(`/sessions/${sessionId}`, { method: "DELETE" });
}

// --- Chat ---
export function sendChat(
  sessionId: string,
  body: ChatRequest
): Promise<ChatResponse> {
  return request(`/sessions/${sessionId}/chat`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getMessages(
  sessionId: string
): Promise<MessageHistoryResponse> {
  return request(`/sessions/${sessionId}/messages`);
}

// --- Compute ---
export function runCompute(sessionId: string): Promise<ComputeResponse> {
  return request(`/sessions/${sessionId}/compute`, { method: "POST" });
}
