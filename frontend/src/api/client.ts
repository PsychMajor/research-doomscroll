import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: '', // Use relative URLs so Vite proxy can intercept in dev mode
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on authentication error
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
