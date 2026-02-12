import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
    (config) => {
        // We need to handle token injection dynamically or via a helper if not stored in cookies/localStorage
        // Since the current implementation uses useAuth context, we might pass the token in the call
        // or rely on a global state. 
        // For now, we will assume the caller attaches the Authorization header or we get it from localStorage if available.

        // Attempt to get token from localStorage if standard auth implementation
        const token = typeof window !== 'undefined' ? localStorage.getItem('supabase-auth-token') : null;
        // Note: detailed Supabase auth usually manages this, but for our custom backend calls:

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Helper to set auth token for a specific request config
export const getAuthConfig = (token) => ({
    headers: {
        Authorization: `Bearer ${token}`
    }
});

export default api;
