import { describe, it, expect, beforeEach } from "vitest";
import { useSessionStore } from "@/stores/sessionStore";

describe("sessionStore", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("initializes with null sessionId", () => {
    expect(useSessionStore.getState().sessionId).toBeNull();
  });

  it("sets sessionId", () => {
    useSessionStore.getState().setSessionId("test-123");
    expect(useSessionStore.getState().sessionId).toBe("test-123");
  });

  it("adds messages", () => {
    useSessionStore.getState().addMessage({
      id: "1",
      role: "user",
      content: "hello",
    });
    expect(useSessionStore.getState().messages).toHaveLength(1);
    expect(useSessionStore.getState().messages[0]?.content).toBe("hello");
  });

  it("sets draft input", () => {
    useSessionStore.getState().setDraftInput({ claim: "test" });
    expect(useSessionStore.getState().draftInput).toEqual({ claim: "test" });
  });

  it("sets compute result", () => {
    useSessionStore.getState().setComputeResult({
      score: 7,
      label: "Strong",
      summary: "Good argument",
      breakdown: {},
    });
    expect(useSessionStore.getState().computeResult?.score).toBe(7);
  });

  it("resets all state", () => {
    useSessionStore.getState().setSessionId("123");
    useSessionStore.getState().addMessage({ id: "1", role: "user", content: "hi" });
    useSessionStore.getState().reset();
    expect(useSessionStore.getState().sessionId).toBeNull();
    expect(useSessionStore.getState().messages).toHaveLength(0);
  });
});
