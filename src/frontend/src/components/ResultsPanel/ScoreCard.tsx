import clsx from "clsx";

interface ScoreCardProps {
  score: number;
  label: string;
}

export function ScoreCard({ score, label }: ScoreCardProps) {
  const colorClass =
    score <= 3 ? "score-weak" : score <= 6 ? "score-moderate" : "score-strong";

  return (
    <div className={clsx("score-card", colorClass)}>
      <div className="score-value">{score}</div>
      <div className="score-max">/10</div>
      <div className="score-label">{label}</div>
    </div>
  );
}
