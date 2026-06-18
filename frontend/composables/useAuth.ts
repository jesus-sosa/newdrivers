export const useAuth = () => {
  const auth = useAuthStore()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const login = async (email: string, password: string) => {
    auth.isLoading = true
    try {
      const response = await $fetch<{
        access_token: string
        token_type: string
        user: {
          id: string
          nombre_completo: string
          email: string
          rol: string
          activo: boolean
          created_at: string
        }
      }>(`${apiBase}/api/auth/login`, {
        method: 'POST',
        body: { email, password },
        credentials: 'include',  // necesario para recibir cookie httpOnly
      })
      auth.setAuth(response.access_token, response.user)
      return { success: true }
    } catch (error: unknown) {
      let errorMessage = 'Error al iniciar sesión'
      if (error && typeof error === 'object') {
        const err = error as Record<string, unknown>
        const data = err.data as Record<string, unknown> | undefined
        if (typeof data?.detail === 'string') errorMessage = data.detail
        else if (typeof err.message === 'string') errorMessage = err.message
      }
      return { success: false, error: errorMessage }
    } finally {
      auth.isLoading = false
    }
  }

  const logout = async () => {
    try {
      await $fetch(`${apiBase}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: auth.accessToken
          ? { Authorization: `Bearer ${auth.accessToken}` }
          : {},
      })
    } finally {
      auth.clearAuth()
      await navigateTo('/login')
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await $fetch<{ access_token: string; token_type: string }>(
        `${apiBase}/api/auth/refresh`,
        {
          method: 'POST',
          credentials: 'include',
        }
      )
      auth.setToken(response.access_token)
      return true
    } catch {
      auth.clearAuth()
      return false
    }
  }

  const fetchMe = async (): Promise<boolean> => {
    if (!auth.accessToken) return false
    try {
      const user = await $fetch<{
        id: string
        nombre_completo: string
        email: string
        rol: string
        activo: boolean
        created_at: string
      }>(`${apiBase}/api/auth/me`, {
        headers: { Authorization: `Bearer ${auth.accessToken}` },
      })
      auth.user = user
      return true
    } catch {
      return false
    }
  }

  return {
    login,
    logout,
    refreshToken,
    fetchMe,
    isAuthenticated: computed(() => auth.isAuthenticated),
    isAdmin: computed(() => auth.isAdmin),
    isEditor: computed(() => auth.isEditor),
    user: computed(() => auth.user),
    isLoading: computed(() => auth.isLoading),
  }
}
