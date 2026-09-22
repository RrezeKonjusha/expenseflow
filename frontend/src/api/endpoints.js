import { api } from './client';

const data = (p) => p.then((r) => r.data);

export const authApi = {
  login: (body) => data(api.post('/auth/login/', body)),
  logout: () => api.post('/auth/logout/'),
  register: (body) => data(api.post('/auth/register/', body)),
  activate: (body) => data(api.post('/auth/activate/', body)),
  forgot: (body) => data(api.post('/auth/password/forgot/', body)),
  reset: (body) => data(api.post('/auth/password/reset/', body)),
  changePassword: (body) => data(api.post('/auth/password/change/', body)),
  me: () => data(api.get('/auth/me/')),
  updateMe: (body) => data(api.patch('/auth/me/', body)),
};

export const expensesApi = {
  list: (params) => data(api.get('/expenses/', { params, paramsSerializer: { indexes: null } })),
  get: (id) => data(api.get(`/expenses/${id}/`)),
  create: (body) => data(api.post('/expenses/', body)),
  update: (id, body) => data(api.patch(`/expenses/${id}/`, body)),
  remove: (id) => api.delete(`/expenses/${id}/`),
  action: (id, name, body) => data(api.post(`/expenses/${id}/${name}/`, body)),
  reimburse: (until) => data(api.post('/expenses/reimburse/', { until })),
  importFile: (file) => {
    const form = new FormData();
    form.append('file', file);
    return data(api.post('/expenses/import/', form));
  },
};

export const usersApi = {
  list: (params) => data(api.get('/users/', { params })),
  create: (body) => data(api.post('/users/', body)),
  update: (id, body) => data(api.patch(`/users/${id}/`, body)),
  deactivate: (id) => api.delete(`/users/${id}/`),
};

export const departmentsApi = {
  list: () => data(api.get('/departments/')),
  create: (body) => data(api.post('/departments/', body)),
  update: (id, body) => data(api.patch(`/departments/${id}/`, body)),
  remove: (id) => api.delete(`/departments/${id}/`),
};

export const projectsApi = {
  list: (params) => data(api.get('/projects/', { params })),
  create: (body) => data(api.post('/projects/', body)),
  update: (id, body) => data(api.patch(`/projects/${id}/`, body)),
  remove: (id) => api.delete(`/projects/${id}/`),
  setMembers: (id, userIds) => data(api.put(`/projects/${id}/members/`, { user_ids: userIds })),
};

export const reportsApi = {
  dashboard: () => data(api.get('/reports/dashboard/')),
  run: (criteria) => data(api.post('/reports/run/', criteria)),
  save: (name, criteria) => data(api.post('/reports/', { name, criteria })),
  list: () => data(api.get('/reports/')),
  get: (id) => data(api.get(`/reports/${id}/`)),
  remove: (id) => api.delete(`/reports/${id}/`),
};

export const auditApi = {
  list: (params) => data(api.get('/audit-logs/', { params })),
};
