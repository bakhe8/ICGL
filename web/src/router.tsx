import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { createRouter, Outlet, RootRoute, Route, redirect } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import AgentPage from './routes/AgentPage';
import AgentsFlowPage from './routes/AgentsFlowPage';
import CapabilitiesPage from './routes/CapabilitiesPage';
import ChatPage from './routes/ChatPage';
import CockpitPage from './routes/CockpitPage';
import ExtendedMindPage from './routes/ExtendedMindPage';
import IdeaRunPage from './routes/IdeaRunPage';
import MindPage from './routes/MindPage';
import OperationsPage from './routes/OperationsPage';

import RoadmapPage from './routes/RoadmapPage';
import SecurityPage from './routes/SecurityPage';
import TimelinePage from './routes/TimelinePage';
import AppShell from './ui/AppShell';

const queryClient = new QueryClient();


const rootRoute = new RootRoute({
  component: () => (
    <QueryClientProvider client={queryClient}>
      <AppShell>
        <Outlet />
      </AppShell>
      <ReactQueryDevtools initialIsOpen={false} />

      <TanStackRouterDevtools position="bottom-right" />
    </QueryClientProvider>
  ),
});

const cockpitRoute = new Route({
  getParentRoute: () => rootRoute,

  path: '/dashboard',
  component: CockpitPage,
});

// Redirect bare /app to the cockpit to avoid blank/404 flashes
const rootIndexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/dashboard' });
  },
});

const agentRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/agent/$agentId',

  component: AgentPage,
});

const chatRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/chat',
  component: ChatPage,

});

const capabilitiesRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/capabilities',
  component: CapabilitiesPage,
});


const ideaRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/idea',
  component: IdeaRunPage,
});


const mindRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/mind',
  component: MindPage,
});

const timelineRoute = new Route({

  getParentRoute: () => rootRoute,
  path: '/timeline',
  component: TimelinePage,
});

const securityRoute = new Route({
  getParentRoute: () => rootRoute,

  path: '/security',
  component: SecurityPage,
});

const opsRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/operations',

  component: OperationsPage,
});

const roadmapRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/roadmap',
  component: RoadmapPage,
});


const extendedMindRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/mind/graph',
  component: ExtendedMindPage,
});

const agentsFlowRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/agents-flow',
  component: AgentsFlowPage,
});

const routeTree = rootRoute.addChildren([
  rootIndexRoute,
  cockpitRoute,
  agentRoute,
  chatRoute,
  capabilitiesRoute,
  ideaRoute,
  mindRoute,
  extendedMindRoute,
  timelineRoute,
  securityRoute,
  opsRoute,
  roadmapRoute,
  agentsFlowRoute,
]);

export const router = createRouter({
  routeTree,
  basepath: '/app',
  defaultPreload: 'intent',
  context: { queryClient },
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
