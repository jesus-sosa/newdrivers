export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  const publicRoutes = ['/login', '/register', '/']
  if (publicRoutes.includes(to.path)) return

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  // Rutas solo para admin
  if (to.path.startsWith('/admin') && auth.user?.rol !== 'admin') {
    return navigateTo('/dashboard')
  }
})
