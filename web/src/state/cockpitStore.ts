import { create } from 'zustand';

export type Panel =
  | 'executive'
  | 'governance'
  | 'archive'
  | 'operations'
  | 'security'
  | 'hr'
  | 'terminal'
  | 'roadmap'
  | 'engineering';

export interface TimelineEvent {
  id: string;
  time: string;
  label: string;
  source?: string;
  severity?: 'info' | 'warn' | 'critical';
}

interface CockpitState {
  activePanel: Panel;
  activeAgentId: string;
  selectedDoc?: string;
  timeline: TimelineEvent[];
  setActivePanel: (panel: Panel) => void;
  setActiveAgent: (id: string) => void;
  setSelectedDoc: (path?: string) => void;
  pushTimeline: (event: TimelineEvent) => void;
  setTimeline: (events: TimelineEvent[]) => void;
}

const useCockpitStore = create<CockpitState>((set) => ({
  activePanel: 'executive',
  activeAgentId: 'secretary',
  selectedDoc: undefined,
  timeline: [],
  setActivePanel: (activePanel) => set({ activePanel }),
  setActiveAgent: (activeAgentId) => set({ activeAgentId }),
  setSelectedDoc: (selectedDoc) => set({ selectedDoc }),
  pushTimeline: (event) =>
    set((state) => ({
      timeline: [event, ...state.timeline].slice(0, 16),
    })),
  setTimeline: (events) => set({ timeline: events }),
}));

export default useCockpitStore;
