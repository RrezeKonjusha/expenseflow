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

let refreshing = null;
export function refreshSession() {
  if (!refreshing) {
    refreshing = axios
      .post('/api/v1/auth/refresh/', null, { withCredentials: true })
      .then((res) => {
        store.dispatch({ type: 'auth/sessionRefreshed', payload: res.data });
        return res.data.access;
      })
      .finally(() => {
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
