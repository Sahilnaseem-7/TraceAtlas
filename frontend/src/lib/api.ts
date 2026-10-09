import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const authApi = {
  login: (email: string, password: string) => api.post('/api/auth/login', null, { params: { email, password } }),
  register: (data: { email: string; password: string; full_name: string }) => api.post('/api/auth/register', data),
  getWorkspaces: () => api.get('/api/auth/workspaces'),
};

export const datasetApi = {
  list: (workspaceId: string) => api.get(`/api/datasets/?workspace_id=${workspaceId}`),
  create: (workspaceId: string, data: any) => api.post(`/api/datasets/?workspace_id=${workspaceId}`, data),
  get: (id: string) => api.get(`/api/datasets/${id}`),
  uploadVersion: (id: string, tag: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/datasets/${id}/versions?version_tag=${tag}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
};

export const lineageApi = {
  getGraph: (workspaceId: string) => api.get(`/api/lineage/graph?workspace_id=${workspaceId}`),
  createEdge: (workspaceId: string, data: any) => api.post(`/api/lineage/edges?workspace_id=${workspaceId}`, data),
  getImpact: (workspaceId: string, sourceType: string, sourceId: string) => 
    api.get(`/api/lineage/impact?workspace_id=${workspaceId}&source_type=${sourceType}&source_id=${sourceId}`),
};

export default api;