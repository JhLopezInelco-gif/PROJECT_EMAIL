import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:7374/api';

// Export API_BASE for direct fetch calls
export const API_BASE = API_URL;

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
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

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  verifyToken: async () => {
    const response = await api.post('/auth/verify');
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Correos API
export const correosAPI = {
  list: async (params = {}) => {
    const response = await api.get('/correos', { params });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/correos/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/correos', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/correos/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/correos/${id}`);
    return response.data;
  },
  deleteAll: async () => {
    const response = await api.delete('/correos');
    return response.data;
  },
  uploadCSV: async (formData) => {
    const response = await api.post('/correos/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getTipos: async () => {
    const response = await api.get('/correos/tipos');
    return response.data;
  },
  validateEmails: async () => {
    const response = await api.post('/correos/validate-emails');
    return response.data;
  },
};

// Emails API
export const emailsAPI = {
  send: async (data) => {
    const response = await api.post('/emails/send', data);
    return response.data;
  },
  getProgress: async (campaignId) => {
    const response = await api.get(`/emails/progress/${campaignId}`);
    return response.data;
  },
  getCampaigns: async (params = {}) => {
    const response = await api.get('/emails/campaigns', { params });
    return response.data;
  },
  getCampaign: async (id) => {
    const response = await api.get(`/emails/campaigns/${id}`);
    return response.data;
  },
  getLogs: async (params = {}) => {
    const response = await api.get('/emails/logs', { params });
    return response.data;
  },
  cancelCampaign: async (id) => {
    const response = await api.post(`/emails/cancel/${id}`);
    return response.data;
  },
  sendTest: async (toEmail, subject, body) => {
    const response = await api.post('/emails/test', null, {
      params: { to_email: toEmail, subject, body },
    });
    return response.data;
  },
  getStats: async () => {
    const response = await api.get('/emails/stats');
    return response.data;
  },
};

export default api;