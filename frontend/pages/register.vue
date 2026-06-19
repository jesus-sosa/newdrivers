<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-header">
        <h1>New Drivers</h1>
        <p>Crea tu cuenta de estudiante</p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="nombre">Nombre completo</label>
          <input
            id="nombre"
            v-model="form.nombre_completo"
            type="text"
            placeholder="Juan Pérez"
            required
            autocomplete="name"
          />
        </div>

        <div class="form-group">
          <label for="email">Correo electrónico</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="tu@email.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="new-password"
          />
        </div>

        <div v-if="error" class="form-error">
          {{ error }}
        </div>

        <button type="submit" class="btn-submit" :disabled="isLoading">
          {{ isLoading ? 'Registrando...' : 'Crear cuenta' }}
        </button>
      </form>

      <p class="register-footer">
        ¿Ya tienes cuenta?
        <NuxtLink to="/login">Inicia sesión</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { register, login, isLoading } = useAuth()
const auth = useAuthStore()

const form = reactive({ nombre_completo: '', email: '', password: '' })
const error = ref('')

onMounted(async () => {
  await auth.hydrateFromStorage()
  if (auth.isAuthenticated) {
    navigateTo(auth.isAdmin || auth.isEditor ? '/admin' : '/dashboard')
  }
})

const handleRegister = async () => {
  error.value = ''
  const result = await register(form.nombre_completo, form.email, form.password)
  if (!result.success) {
    error.value = result.error ?? 'Error al registrar cuenta'
    return
  }
  // Auto-login after successful registration
  const loginResult = await login(form.email, form.password)
  if (loginResult.success) {
    navigateTo('/dashboard')
  } else {
    navigateTo('/login')
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  padding: 1rem;
}

.register-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a56db;
  margin: 0 0 0.25rem;
}

.register-header p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  padding: 0.625rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s;
}

.form-group input:focus {
  border-color: #1a56db;
  box-shadow: 0 0 0 3px rgba(26,86,219,0.1);
}

.form-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.btn-submit {
  background: #1a56db;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-submit:hover:not(:disabled) {
  background: #1e429f;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  margin: 1.25rem 0 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.register-footer a {
  color: #1a56db;
  text-decoration: none;
  font-weight: 500;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>
