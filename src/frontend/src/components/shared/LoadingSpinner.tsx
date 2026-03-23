interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
}

export function LoadingSpinner({ size = "md", label }: LoadingSpinnerProps) {
  return (
    <div className={`spinner spinner-${size}`} role="status">
      <span className="sr-only">{label || "Loading..."}</span>
    </div>
  );
}
