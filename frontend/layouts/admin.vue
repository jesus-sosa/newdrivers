<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <NuxtLink to="/admin">New Drivers</NuxtLink>
        <span class="sidebar-badge">Admin</span>
      </div>

      <nav class="sidebar-nav">
        <NuxtLink to="/admin" class="nav-link" exact-active-class="nav-link--active">
          Dashboard
        </NuxtLink>
        <NuxtLink to="/admin/preguntas" class="nav-link" active-class="nav-link--active">
          Preguntas
        </NuxtLink>
        <NuxtLink to="/admin/configuracion" class="nav-link" active-class="nav-link--active">
          Configuración
        </NuxtLink>
        <NuxtLink to="/admin/usuarios" class="nav-link" active-class="nav-link--active">
          Usuarios
        </NuxtLink>
      </nav>

      <div class="sidebar-footer">
        <div class="sidebar-user">
          <span class="sidebar-user-name">{{ auth.user?.nombre_completo }}</span>
          <span class="sidebar-user-role">{{ auth.user?.rol }}</span>
        </div>
        <button class="sidebar-logout" @click="handleLogout">Salir</button>
      </div>
    </aside>

    <div class="admin-content">
      <header class="admin-topbar">
        <slot name="title">
          <h1 class="page-title">Panel de Administración</h1>
        </slot>
      </header>

      <main class="admin-main">
        <slot />
      </main>
    </div>
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
.admin-layout {
  display: flex;
  min-height: 100vh;
  font-family: system-ui, -apple-system, sans-serif;
  background: #f9fafb;
}

.admin-sidebar {
  width: 240px;
  background: #1e293b;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-brand {
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-brand a {
  color: white;
  text-decoration: none;
  font-weight: 700;
  font-size: 1rem;
}

.sidebar-badge {
  font-size: 0.625rem;
  background: #1a56db;
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
}

.nav-link {
  color: #94a3b8;
  text-decoration: none;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  transition: all 0.15s;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.05);
}

.nav-link--active {
  color: white;
  background: rgba(255,255,255,0.08);
  border-left-color: #1a56db;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #334155;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar-user {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.sidebar-user-name {
  font-size: 0.875rem;
  color: white;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-user-role {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: capitalize;
}

.sidebar-logout {
  background: transparent;
  color: #64748b;
  border: 1px solid #334155;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.15s;
  text-align: left;
}

.sidebar-logout:hover {
  color: white;
  border-color: #475569;
}

.admin-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-topbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.admin-main {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
</style>
