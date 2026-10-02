/**
 * Axios client.
 * - Adds the in-memory access token to every request.
 * - On a 401, calls /auth/refresh/ once (the refresh token is an httpOnly cookie),
 *   then replays the original request. Parallel 401s share the same refresh call.
 */
import axios from 'axios';

let store;
export const injectStore = (s) => {
  store = s;
};

export const api = axios.create({ baseURL: '/api/v1', withCredentials: true });

api.interceptors.request.use((config) => {
  const token = store?.getState().auth.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/*
 * Refresh rotation blacklists the old refresh token on every call, so two pages must never send the same one.
 * - keepalive: if the page is reloaded mid-call, the browser still finishes it and stores the rotated cookie.
 * - A page that starts within 2 s of another page's refresh waits for it (localStorage marker), so it sends the
 *   new cookie instead of the blacklisted one.
 * - Web Locks serialise refreshes between open tabs.
 */
const MARK_KEY = 'ef:refresh';
const GRACE_MS = 2000;

const readMark = () => {
  try {
    return JSON.parse(localStorage.getItem(MARK_KEY)) || {};
  } catch {
    return {};
  }
};
const writeMark = (mark) => {
  try {
    localStorage.setItem(MARK_KEY, JSON.stringify(mark));
  } catch {
    // storage unavailable (private mode): fall back to the plain refresh
  }
};
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForOtherRefresh() {
  const { started, done } = readMark();
  if (!started || done >= started) return;
  const until = started + GRACE_MS;
  while (Date.now() < until && !(readMark().done >= started)) await sleep(100);
}

async function rotate() {
  await waitForOtherRefresh();
  const started = Date.now();
  writeMark({ started });
  try {
    const res = await fetch('/api/v1/auth/refresh/', {
      method: 'POST',
      credentials: 'include',
      keepalive: true,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok)
      throw Object.assign(new Error(data.detail || 'Session expired'), {
        response: { status: res.status, data },
      });
    store.dispatch({ type: 'auth/sessionRefreshed', payload: data });
    return data.access;
  } finally {
    writeMark({ started, done: Date.now() });
  }
}

let refreshing = null;
export function refreshSession() {
  if (!refreshing) {
    const run = navigator.locks ? navigator.locks.request('ef-refresh', rotate) : rotate();
    refreshing = run.finally(() => {
      refreshing = null;
    });
  }
  return refreshing;
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isAuthCall = original?.url?.startsWith('/auth/');
    if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      try {
        const access = await refreshSession();
        original.headers.Authorization = `Bearer ${access}`;
        return api(original);
      } catch {
        store.dispatch({ type: 'auth/loggedOut' });
      }
    }
    return Promise.reject(error);
  },
);

export const errorMessage = (err) => err?.response?.data?.detail || err?.message || 'Something went wrong';
export const fieldErrors = (err) => err?.response?.data?.errors || {};

/** Put server-side field errors into react-hook-form. Returns true if any were applied. */
export function applyFieldErrors(err, setError) {
  const errors = fieldErrors(err);
  let applied = false;
  Object.entries(errors).forEach(([field, messages]) => {
    const message = Array.isArray(messages) ? messages.join(' ') : String(messages);
    setError(field === 'non_field_errors' ? 'root' : field, { type: 'server', message });
    applied = true;
  });
  return applied;
}

/** Download a file from an authenticated endpoint. */
export async function download(url, params, fallbackName) {
  const res = await api.get(url, { params, responseType: 'blob' });
  const disposition = res.headers['content-disposition'] || '';
  const name = /filename="?([^"]+)"?/.exec(disposition)?.[1] || fallbackName;
  const href = URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = href;
  a.download = name;
  a.click();
  URL.revokeObjectURL(href);
}
