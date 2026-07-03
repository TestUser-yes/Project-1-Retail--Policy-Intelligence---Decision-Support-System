import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get token from localStorage
const getToken = () => localStorage.getItem('authToken');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Add auth header to all requests
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const queryAPI = {
  // Get demo token for authentication
  getToken: async () => {
    const response = await api.get('/token');
    localStorage.setItem('authToken', response.data.access_token);
    return response.data;
  },

  ask: async (query) => {
    // Ensure we have a token
    const token = getToken();
    if (!token) {
      await queryAPI.getToken();
    }
    const response = await api.post('/ask', { query });
    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
