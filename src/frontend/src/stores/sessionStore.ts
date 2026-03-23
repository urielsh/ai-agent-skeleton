/** Session state store (Zustand). */

import { create } from "zustand";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ComputeResult {
  score: number;
  label: string;
  summary: string;
  breakdown: Record<string, unknown>;
}

interface SessionState {
  sessionId: string | null;
  messages: ChatMessage[];
  draftInput: Record<string, unknown>;
  missingFields: string[];
  computeResult: ComputeResult | null;
  setSessionId: (id: string | null) => void;
  addMessage: (msg: ChatMessage) => void;
  setDraftInput: (draft: Record<string, unknown>) => void;
  setMissingFields: (fields: string[]) => void;
  setComputeResult: (result: ComputeResult | null) => void;
  reset: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  messages: [],
  draftInput: {},
  missingFields: [],
  computeResult: null,
  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  setDraftInput: (draft) => set({ draftInput: draft }),
  setMissingFields: (fields) => set({ missingFields: fields }),
  setComputeResult: (result) => set({ computeResult: result }),
  reset: () =>
    set({
      sessionId: null,
      messages: [],
      draftInput: {},
      missingFields: [],
      computeResult: null,
    }),
}));
