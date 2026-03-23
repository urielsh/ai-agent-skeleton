/** UI state store (Zustand). */

import { create } from "zustand";

type RightPanel = "chat" | "results";

interface UiState {
  rightPanel: RightPanel;
  isMobileSidebarOpen: boolean;
  setRightPanel: (panel: RightPanel) => void;
  toggleMobileSidebar: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  rightPanel: "chat",
  isMobileSidebarOpen: false,
  setRightPanel: (panel) => set({ rightPanel: panel }),
  toggleMobileSidebar: () =>
    set((s) => ({ isMobileSidebarOpen: !s.isMobileSidebarOpen })),
}));
