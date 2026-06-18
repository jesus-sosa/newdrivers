import { defineStore } from 'pinia'

interface User {
  id: string
  nombre_completo: string
  email: string
  rol: string
  activo: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    isLoading: false,
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.accessToken && !!state.user,
    isAdmin: (state): boolean => state.user?.rol === 'admin',
    isEditor: (state): boolean => state.user?.rol === 'editor',
    isEstudiante: (state): boolean => state.user?.rol === 'estudiante',
  },

  actions: {
    setAuth(token: string, user: User) {
      this.accessToken = token
      this.user = user
      if (process.client) {
        localStorage.setItem('access_token', token)
      }
    },

    clearAuth() {
      this.accessToken = null
      this.user = null
      if (process.client) {
        localStorage.removeItem('access_token')
      }
    },

    async hydrateFromStorage() {
      if (!process.client) return
      const token = localStorage.getItem('access_token')
      if (!token) return
      this.accessToken = token
    },
  },
})
