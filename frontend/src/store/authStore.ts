import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
    id: string;
    email: string;
    full_name: string;
}

interface AuthState {
    token: string | null;
    user: User | null;
    setAuth: (token: string, user: User) => void;
    logout: () => void;
    isAuthenticated: () => boolean;
    fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: 'bypass-token',
            user: {
                id: 'demo-id',
                email: 'demo@student.com',
                full_name: 'Demo Student'
            },
            setAuth: (token, user) => set({ token, user }),
            logout: () => set({ token: null, user: null }),
            isAuthenticated: () => true, // Always true for direct access
            fetchUser: async () => {
                // No-op for bypass mode
            },
        }),
        {
            name: 'auth-storage',
        }
    )
);
