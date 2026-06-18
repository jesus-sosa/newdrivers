<template>
  <div class="app-layout">
    <header class="app-header">
      <nav class="nav-container">
        <div class="nav-brand">
          <NuxtLink to="/">New Drivers</NuxtLink>
        </div>
        <div class="nav-actions">
          <template v-if="auth.isAuthenticated">
            <span class="nav-user">{{ auth.user?.nombre_completo }}</span>
            <button class="btn-logout" @click="handleLogout">Cerrar sesión</button>
          </template>
          <template v-else>
            <NuxtLink to="/login" class="btn-login">Iniciar sesión</NuxtLink>
          </template>
        </div>
      </nav>
    </header>

    <main class="app-main">
      <slot />
    </main>

    <footer class="app-footer">
      <p>© {{ new Date().getFullYear() }} New Drivers — Simulador de Examen</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const { logout } = useAuth()

const handleLogout = async () => {
  await logout()
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: system-ui, -apple-system, sans-serif;
}

.app-header {
  background: #1a56db;
  color: white;
  padding: 0 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand a {
  color: white;
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-user {
  font-size: 0.875rem;
  opacity: 0.9;
}

.btn-logout {
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.15s;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.25);
}

.btn-login {
  color: white;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.app-footer {
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  text-align: center;
  padding: 1rem;
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
