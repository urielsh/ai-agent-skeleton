import { useNavigate } from "react-router-dom";
import { useCreateSession } from "@/api/hooks";
import { AppLayout } from "@/components/Layout/AppLayout";

export function LandingPage() {
  const navigate = useNavigate();
  const createSession = useCreateSession();

  const handleStart = () => {
    createSession.mutate(undefined, {
      onSuccess: (data) => {
        navigate(`/session/${data.session_id}`);
      },
    });
  };

  return (
    <AppLayout>
      <div className="landing">
        <div className="landing-hero">
          <h1>AI Agent Skeleton</h1>
          <p className="landing-subtitle">
            A full-stack template for building AI-powered analysis agents.
            Chat &rarr; Collect Input &rarr; Run Engine &rarr; See Results.
          </p>
          <button
            className="btn btn-primary btn-lg"
            onClick={handleStart}
            disabled={createSession.isPending}
          >
            {createSession.isPending ? "Creating..." : "Start New Session"}
          </button>
          {createSession.isError && (
            <p className="error-text">
              Failed to create session. Is the backend running?
            </p>
          )}
        </div>

        <div className="landing-features">
          <div className="feature-card">
            <h3>Guided Input</h3>
            <p>LLM-powered chat collects structured input through conversation.</p>
          </div>
          <div className="feature-card">
            <h3>Deterministic Engine</h3>
            <p>Sample blackbox engine scores arguments. Replace with your own logic.</p>
          </div>
          <div className="feature-card">
            <h3>Full Stack</h3>
            <p>FastAPI + React + PostgreSQL + Redis. Docker Compose ready.</p>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
