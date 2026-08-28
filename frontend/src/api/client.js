import axios from 'axios';

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '');

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('shadow_ai_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 and 403 globally
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;
    if (response) {
      if (response.status === 401) {
        // Clear stale credentials and redirect to login
        localStorage.removeItem('shadow_ai_token');
        localStorage.removeItem('shadow_ai_user');
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login?expired=1';
        }
      } else if (response.status === 403) {
        // Forbidden due to role permission mismatch
        if (window.location.pathname !== '/not-authorized') {
          window.location.href = '/not-authorized';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;
