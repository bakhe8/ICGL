import { create } from 'zustand';

export interface TimelineEvent {
  id: string;
  time: string;
  label: string;
  source?: string;
  severity?: 'info' | 'warn' | 'critical';
}

interface CockpitState {
  activeAgentId: string;
  selectedDoc?: string;
  timeline: TimelineEvent[];
  setActiveAgent: (id: string) => void;
  setSelectedDoc: (path?: string) => void;
  pushTimeline: (event: TimelineEvent) => void;
  setTimeline: (events: TimelineEvent[]) => void;
}

const useCockpitStore = create<CockpitState>((set) => ({
  activeAgentId: 'secretary',
  selectedDoc: undefined,
  timeline: [],
  setActiveAgent: (activeAgentId) => set({ activeAgentId }),
  setSelectedDoc: (selectedDoc) => set({ selectedDoc }),
  pushTimeline: (event) =>
    set((state) => ({
      timeline: [event, ...state.timeline].slice(0, 16),
    })),
  setTimeline: (events) => set({ timeline: events }),
}));

export default useCockpitStore;
