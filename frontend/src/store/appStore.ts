import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/lib/auth';

interface AppState {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: 'datagov-storage',
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);