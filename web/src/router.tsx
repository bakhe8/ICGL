import { createRouter, Outlet, RootRoute, Route } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import CockpitPage from './routes/CockpitPage';
import AgentPage from './routes/AgentPage';
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
  path: '/',
  component: CockpitPage,
});

const agentRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/agent/$agentId',
  component: AgentPage,
});

const routeTree = rootRoute.addChildren([cockpitRoute, agentRoute]);

export const router = createRouter({
  routeTree,
  basepath: '/dashboard',
  context: { queryClient },
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
