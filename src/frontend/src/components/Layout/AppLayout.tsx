import type { ReactNode } from "react";
import { Header } from "./Header";

interface AppLayoutProps {
  children: ReactNode;
  sessionActive?: boolean;
  onEndSession?: () => void;
}

export function AppLayout({ children, sessionActive, onEndSession }: AppLayoutProps) {
  return (
    <div className="app-layout">
      <Header sessionActive={sessionActive} onEndSession={onEndSession} />
      <main className="app-main">{children}</main>
    </div>
  );
}
