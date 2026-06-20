<template>
  <div class="new-student-page">
    <div class="new-student-page__header">
      <NuxtLink to="/admin/usuarios" class="back-link">
        &larr; Volver a estudiantes
      </NuxtLink>
      <h1 class="page-title">Agregar Estudiante</h1>
    </div>

    <!-- Error banner -->
    <div v-if="errorMessage" class="error-banner">
      {{ errorMessage }}
      <button class="banner-close" @click="errorMessage = null">&#10005;</button>
    </div>

    <div class="form-card">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="nombre_completo">Nombre completo</label>
          <input
            id="nombre_completo"
            v-model="form.nombre_completo"
            type="text"
            class="form-input"
            placeholder="Nombre y apellidos del estudiante"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="correo@ejemplo.com"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Contraseña temporal</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="Contraseña temporal para el estudiante"
            required
            minlength="8"
          />
        </div>

        <div class="form-actions">
          <NuxtLink to="/admin/usuarios" class="btn btn--secondary">
            Cancelar
          </NuxtLink>
          <button type="submit" class="btn btn--primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Guardando...' : 'Crear estudiante' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const auth = useAuthStore()
const runtimeConfig = useRuntimeConfig()
const apiBase = runtimeConfig.public.apiBase
const router = useRouter()

const form = ref({
  nombre_completo: '',
  email: '',
  password: '',
})

const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function handleSubmit() {
  errorMessage.value = null
  isSubmitting.value = true

  try {
    await $fetch(`${apiBase}/api/admin/students`, {
      method: 'POST',
      headers: getHeaders(),
      body: {
        nombre_completo: form.value.nombre_completo,
        email: form.value.email,
        password: form.value.password,
      },
    })
    router.push('/admin/usuarios?created=1')
  } catch (error: unknown) {
    let msg = 'Error al crear el estudiante'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    errorMessage.value = msg
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.new-student-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 540px;
}

.new-student-page__header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.back-link {
  font-size: 0.875rem;
  color: #2563eb;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 1rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.15);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
  text-decoration: none;
}

.btn--primary {
  background: #1a56db;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: #1e40af;
}

.btn--secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--secondary:hover {
  background: #f9fafb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.banner-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: inherit;
  opacity: 0.7;
  padding: 0 0.25rem;
  flex-shrink: 0;
}

.banner-close:hover {
  opacity: 1;
}
</style>
