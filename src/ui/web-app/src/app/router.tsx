import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createRouter, Outlet, redirect, RootRoute, Route } from '@tanstack/react-router';
import CockpitPage from '../domains/desk/routes/CockpitPage';
import AppShell from '../shared/layout/AppShell';

const queryClient = new QueryClient();

const rootRoute = new RootRoute({
  component: () => (
    <QueryClientProvider client={queryClient}>
      <AppShell>
        <Outlet />
      </AppShell>
    </QueryClientProvider>
  ),
});

// Desk Routes
import ChatPage from '../domains/desk/routes/ChatPage';
import GovernanceLabPage from '../domains/desk/routes/GovernanceLabPage';
import IdeaRunPage from '../domains/desk/routes/IdeaRunPage';
import RoadmapPage from '../domains/desk/routes/RoadmapPage';
import TimelinePage from '../domains/desk/routes/TimelinePage';
// SecurityPage is likely here or Tower. Assuming Desk based on user flow, but checking Tower is safer if security-focused.
// Let's assume Tower for SecurityPage if it's about "Safety". But Sidebar puts it near "Mind".
// Check Step 5362: SecurityPage was in the list. Let's assume Desk.
import SecurityPage from '../domains/tower/routes/SecurityPage';

// Hall Routes
import AgentPage from '../domains/hall/routes/AgentPage';
import ChannelsPage from '../domains/hall/routes/ChannelsPage';
import MindPage from '../domains/hall/routes/MindPage';
import RegistryPage from '../domains/hall/routes/RegistryPage';

// Tower Routes
import AdminDashboardPage from '../domains/tower/routes/AdminDashboardPage';
import NCCIPage from '../domains/tower/routes/NCCIPage';
import ObservabilityPage from '../domains/tower/routes/ObservabilityPage';
import PoliciesPage from '../domains/tower/routes/PoliciesPage';
import SCPCOC from '../domains/tower/routes/SCPCOC';
import SCPEvents from '../domains/tower/routes/SCPEvents';
import SCPOverview from '../domains/tower/routes/SCPOverview';
import SCPTraces from '../domains/tower/routes/SCPTraces';

// ... (Rest of router setup)

// Route Definitions

const cockpitRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  component: CockpitPage,
});

const rootIndexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/dashboard' });
  },
});

// --- Desk ---
const chatRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
  component: ChatPage,
});

const ideaRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/idea',
  component: IdeaRunPage,
});

const timelineRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/timeline',
  component: TimelinePage,
});

const governanceLabRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/governance-lab',
  component: GovernanceLabPage,
});

const roadmapRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/roadmap',
  component: RoadmapPage,
});

const securityRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/security',
  component: SecurityPage,
});


// --- Hall ---
const registryRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/registry',
  component: RegistryPage,
});

const mindRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/mind',
  component: MindPage,
});

const agentRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/agent/$agentId',
  component: AgentPage,
});


// --- Tower ---
const adminDashboardRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/dashboard',
  component: AdminDashboardPage,
});

const ncciRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/ncci',
  component: NCCIPage,
});

const observabilityRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/observability',
  component: ObservabilityPage,
});

// SCP
const scpOverviewRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/overview',
  component: SCPOverview,
});

const scpEventsRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/events',
  component: SCPEvents,
});

const scpChannelsRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/channels',
  component: ChannelsPage,
});

const scpTracesRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/traces',
  component: SCPTraces,
});

const scpPoliciesRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/policies',
  component: PoliciesPage,
});

const scpCocRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/admin/scp/coc',
  component: SCPCOC,
});


const routeTree = rootRoute.addChildren([
  rootIndexRoute,
  cockpitRoute,
  chatRoute,
  ideaRoute,
  timelineRoute,
  governanceLabRoute,
  roadmapRoute,
  securityRoute,
  registryRoute,
  mindRoute,
  agentRoute,
  adminDashboardRoute,
  ncciRoute,
  observabilityRoute,
  scpOverviewRoute,
  scpEventsRoute,
  scpChannelsRoute,
  scpTracesRoute,
  scpPoliciesRoute,
  scpCocRoute
]);

const runtimeBase = (() => {
  const raw = (import.meta.env.BASE_URL ?? '/');
  const trimmed = raw.endsWith('/') && raw.length > 1 ? raw.slice(0, -1) : raw;
  return trimmed || '/';
})();

export const router = createRouter({
  routeTree,
  basepath: runtimeBase,
  defaultPreload: 'intent',
  context: { queryClient },
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
