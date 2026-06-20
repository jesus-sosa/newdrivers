export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  const publicRoutes = ['/login', '/register', '/']
  if (publicRoutes.includes(to.path)) return

  if (!auth.isAuthenticated) {
    return navigateTo('/login')
  }

  // Rutas solo para admin y editor
  if (to.path.startsWith('/admin') && !auth.isAdmin && !auth.isEditor) {
    return navigateTo('/dashboard')
  }
})
