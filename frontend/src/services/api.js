import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // Health check
  health: () => api.get('/health'),
  
  // Auth endpoints
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  logout: () => api.post('/api/auth/logout'),
  getCurrentUser: () => api.get('/api/auth/me'),
  getAllUsers: (params) => api.get('/api/auth/users', { params }),
  
  // Projects endpoints
  getProjects: (params) => api.get('/api/projects', { params }),
  getProject: (id) => api.get(`/api/projects/${id}`),
  createProject: (data) => api.post('/api/projects', data),
  updateProject: (id, data) => api.put(`/api/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/api/projects/${id}`),
  createDemoProject: () => api.post('/api/projects/demo'),
  
  // Tasks endpoints
  getTasks: (params) => api.get('/api/tasks', { params }),
  getTask: (id) => api.get(`/api/tasks/${id}`),
  createTask: (data) => api.post('/api/tasks', data),
  updateTask: (id, data) => api.put(`/api/tasks/${id}`, data),
  updateTaskProgress: (id, progress) => api.patch(`/api/tasks/${id}/progress`, { progress }),
  deleteTask: (id) => api.delete(`/api/tasks/${id}`),
  
  // Forecast endpoints
  getForecasts: (params) => api.get('/api/forecasts', { params }),
  getLatestForecasts: () => api.get('/api/forecasts/latest'),
  analyzeForecast: (projectId) => api.post('/api/forecasts/analyze', null, { 
    params: projectId ? { project_id: projectId } : {} 
  }),
  
  // Simulation endpoints
  getSimulations: (params) => api.get('/api/simulations', { params }),
  runSimulation: (data) => api.post('/api/simulations/run', data),
  
  // Automation logs endpoints
  getAutomationLogs: (params) => api.get('/api/automation-logs', { params }),
  getAutomationLog: (id) => api.get(`/api/automation-logs/${id}`),
};

export default api;
