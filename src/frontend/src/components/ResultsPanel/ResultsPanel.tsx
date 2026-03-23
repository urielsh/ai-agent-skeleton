import { useSessionStore } from "@/stores/sessionStore";
import { useCompute } from "@/api/hooks";
import { ScoreCard } from "./ScoreCard";

interface ResultsPanelProps {
  sessionId: string;
}

export function ResultsPanel({ sessionId }: ResultsPanelProps) {
  const computeResult = useSessionStore((s) => s.computeResult);
  const missingFields = useSessionStore((s) => s.missingFields);
  const setComputeResult = useSessionStore((s) => s.setComputeResult);
  const computeMutation = useCompute(sessionId);

  const canCompute = missingFields.length === 0;

  const handleCompute = () => {
    computeMutation.mutate(undefined, {
      onSuccess: (data) => {
        setComputeResult({
          score: data.score,
          label: data.label,
          summary: data.summary,
          breakdown: data.breakdown,
        });
      },
    });
  };

  return (
    <div className="results-panel">
      <h2 className="results-title">Analysis Results</h2>

      {!computeResult && (
        <div className="results-empty">
          {canCompute ? (
            <>
              <p>All required fields collected. Ready to analyze.</p>
              <button
                className="btn btn-primary"
                onClick={handleCompute}
                disabled={computeMutation.isPending}
              >
                {computeMutation.isPending ? "Analyzing..." : "Run Analysis"}
              </button>
            </>
          ) : (
            <p>
              Complete the conversation to collect all required fields:
              {" "}{missingFields.join(", ")}
            </p>
          )}
          {computeMutation.isError && (
            <p className="error-text">
              Error: {computeMutation.error.message}
            </p>
          )}
        </div>
      )}

      {computeResult && (
        <>
          <ScoreCard
            score={computeResult.score}
            label={computeResult.label}
          />
          <div className="results-summary">
            <h3>Summary</h3>
            <p>{computeResult.summary}</p>
          </div>
          <button
            className="btn btn-secondary"
            onClick={handleCompute}
            disabled={computeMutation.isPending}
          >
            Re-analyze
          </button>
        </>
      )}
    </div>
  );
}
