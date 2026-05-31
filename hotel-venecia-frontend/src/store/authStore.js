import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      setSession: ({ user, token }) => {
        localStorage.setItem('hotel_token', token || '')
        set({ user, token })
      },
      clearSession: () => {
        localStorage.removeItem('hotel_token')
        set({ user: null, token: null })
      },
    }),
    { name: 'hotel_auth_store' },
  ),
)
