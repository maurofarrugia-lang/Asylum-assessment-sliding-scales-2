import { Assessment, Country, SummaryResponse } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const TOKEN_KEY = 'asylum-token';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string) {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearStoredToken() {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(TOKEN_KEY);
  }
}

async function getToken(): Promise<string> {
  const token = getStoredToken();
  if (!token) {
    throw new Error('You are not signed in. Use the officer sign-in page first.');
  }
  return token;
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Sign-in failed.');
  }

  const data = await response.json();
  setStoredToken(data.access_token);
  return data;
}

async function apiFetch<T>(path: string, init?: RequestInit, needsAuth = true): Promise<T> {
  const token = needsAuth ? await getToken() : undefined;
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(needsAuth && token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers || {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed for ${path}`);
  }
  return response.json();
}

export const api = {
  health: () => apiFetch<{ status: string; environment: string }>('/health', undefined, false),
  getGeoTree: () => apiFetch<Country[]>('/api/geographies/tree'),
  getSummary: (geoType: string, geoId: number | null, months: number, customAreaName?: string) => {
    const params = new URLSearchParams({ geo_type: geoType, months: String(months) });
    if (geoId) params.set('geo_id', String(geoId));
    if (customAreaName) params.set('custom_area_name', customAreaName);
    return apiFetch<SummaryResponse>(`/api/incidents/summary?${params.toString()}`);
  },
  generateAssessment: (payload: unknown) =>
    apiFetch<Assessment>('/api/assessments/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAssessments: () => apiFetch<Assessment[]>('/api/assessments'),
  getThresholds: () => apiFetch('/api/thresholds'),
  getSources: () => apiFetch('/api/sources/verification'),
  runSourceSync: (payload: unknown) =>
    apiFetch('/api/source-sync/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};
