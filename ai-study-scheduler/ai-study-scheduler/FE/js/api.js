export const API_BASE_URL = 'http://127.0.0.1:8000/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg || item.message).filter(Boolean).join(', ')
      : data.detail;
    throw new Error(detail || data.error || `API trả về lỗi ${response.status}`);
  }
  return data;
}

export const api = {
  dashboard: () => request('/dashboard'),
  subjects: () => request('/subjects'),
  addSubject: (payload) => request('/subjects', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  tasks: () => request('/tasks'),
  addTask: (payload) => request('/tasks', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
  updateTaskStatus: (id, status) => request(`/tasks/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),

  availability: () => request('/availability'),
  addAvailability: (payload) => request('/availability', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  deleteAvailability: (id) => request(`/availability/${id}`, { method: 'DELETE' }),

  schedule: () => request('/schedule'),
  generateSchedule: () => request('/schedule/generate', { method: 'POST' }),
  updateSessionStatus: (id, status) => request(`/sessions/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
};
