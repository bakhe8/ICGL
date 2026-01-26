# UI Components Library

Scaffolded package for shared React UI pieces.

- Entry point: `src/index.ts` (currently placeholder export).
- مكونات منقولة: `Mermaid`, `TechnicalCapabilities`, `WorkspaceSelector`, `TaskTracker`, `SovereignTerminal`, `CouncilGrid`, `ADRFeed`, `MetricsGrid`, `PolicyEditor` (+ CSS), `TraceVisualization` (+ CSS), مكونات المحادثة (`MessageBubble`, `ThinkingBlock`, `ChatConsole`).
- Target sources القادمة: `ui/web/app/components` و `ui/web/app/ui`.
- Package metadata lives in `package.json` with React peer deps to keep interfaces stable.

Wire lint/build when components start landing (tsup/tsc + eslint).
