import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useSessionStore } from "@/stores/sessionStore";
import { useUiStore } from "@/stores/uiStore";
import { useDeleteSession } from "@/api/hooks";
import { AppLayout } from "@/components/Layout/AppLayout";
import { ChatPanel } from "@/components/ChatPanel/ChatPanel";
import { ResultsPanel } from "@/components/ResultsPanel/ResultsPanel";

export function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const rightPanel = useUiStore((s) => s.rightPanel);
  const setRightPanel = useUiStore((s) => s.setRightPanel);
  const storeSessionId = useSessionStore((s) => s.sessionId);
  const setSessionId = useSessionStore((s) => s.setSessionId);
  const reset = useSessionStore((s) => s.reset);
  const deleteMutation = useDeleteSession();

  useEffect(() => {
    if (sessionId && sessionId !== storeSessionId) {
      reset();
      setSessionId(sessionId);
    }
  }, [sessionId, storeSessionId, setSessionId, reset]);

  const handleEndSession = () => {
    if (!sessionId) return;
    deleteMutation.mutate(sessionId, {
      onSuccess: () => {
        reset();
        navigate("/");
      },
    });
  };

  if (!sessionId) {
    navigate("/");
    return null;
  }

  return (
    <AppLayout sessionActive onEndSession={handleEndSession}>
      <div className="session-layout">
        <div className="session-tabs">
          <button
            className={`tab ${rightPanel === "chat" ? "tab-active" : ""}`}
            onClick={() => setRightPanel("chat")}
          >
            Chat
          </button>
          <button
            className={`tab ${rightPanel === "results" ? "tab-active" : ""}`}
            onClick={() => setRightPanel("results")}
          >
            Results
          </button>
        </div>
        <div className="session-content">
          {rightPanel === "chat" ? (
            <ChatPanel sessionId={sessionId} />
          ) : (
            <ResultsPanel sessionId={sessionId} />
          )}
        </div>
      </div>
    </AppLayout>
  );
}
