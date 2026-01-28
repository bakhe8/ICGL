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

const routeTree = rootRoute.addChildren([
  rootIndexRoute,
  cockpitRoute,
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
