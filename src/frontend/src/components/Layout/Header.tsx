interface HeaderProps {
  sessionActive?: boolean;
  onEndSession?: () => void;
}

export function Header({ sessionActive, onEndSession }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-left">
        <a href="/" className="header-logo">
          AI Agent Skeleton
        </a>
      </div>
      <div className="header-right">
        {sessionActive && onEndSession && (
          <button className="btn btn-secondary btn-sm" onClick={onEndSession}>
            End Session
          </button>
        )}
      </div>
    </header>
  );
}
