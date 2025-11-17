import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: '', // Use relative URLs so Vite proxy can intercept in dev mode
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
    });
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      dataType: typeof response.data,
      dataLength: Array.isArray(response.data) ? response.data.length : 'N/A',
    });
    return response;
  },
  (error) => {
    const errorDetails = {
      message: error.message,
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      params: error.config?.params,
    };
    
    console.error('API Error:', errorDetails);
    
    if (error.response?.status === 401) {
      console.warn('Unauthorized - user needs to login');
      // Don't auto-redirect - let the user click the login button
      // The login button will handle the redirect to /api/auth/login
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
