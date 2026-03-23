/** React Query hooks for the API. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createSession,
  deleteSession,
  getHealth,
  getSession,
  runCompute,
  sendChat,
} from "./client";
import type { ChatRequest, ChatResponse, ComputeResponse } from "./types";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    staleTime: 30_000,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useSession(sessionId: string | null) {
  return useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => getSession(sessionId!),
    enabled: !!sessionId,
    staleTime: 10_000,
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteSession,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
}

export function useSendChat(sessionId: string) {
  return useMutation<ChatResponse, Error, ChatRequest>({
    mutationFn: (body) => sendChat(sessionId, body),
  });
}

export function useCompute(sessionId: string) {
  return useMutation<ComputeResponse, Error, void>({
    mutationFn: () => runCompute(sessionId),
  });
}
