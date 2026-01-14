import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
    // Rely on Zustand's persist key in localStorage
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
        try {
            const { state } = JSON.parse(authStorage);
            if (state?.token) {
                config.headers.Authorization = `Bearer ${state.token}`;
            }
        } catch (e) {
            console.error("Failed to parse auth token", e);
        }
    }
    return config;
});

export default api;
