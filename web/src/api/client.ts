const rawBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? '';
const apiBase = rawBase.replace(/\/$/, '');

const normalizePath = (path: string) => (path.startsWith('/') ? path : `/${path}`);

export const apiUrl = (path: string) => `${apiBase}${normalizePath(path)}`;

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function postJson<T>(path: string, body: any, init?: RequestInit): Promise<T> {
  return fetchJson<T>(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    body: JSON.stringify(body),
    ...init,
  });
}

export function resolveWsUrl(path: string): string {
  const base = apiBase || window.location.origin;
  const url = new URL(base.startsWith('http') ? base : `${window.location.origin}${base || ''}`);
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  url.pathname = normalizePath(path);
  return url.toString();
}
