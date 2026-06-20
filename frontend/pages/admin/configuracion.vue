<template>
  <div class="config-page">
    <h1 class="page-title">Configuración del Examen</h1>

    <!-- Unconfigured warning banner -->
    <div v-if="config && config.porcentaje_aprobacion === null" class="warning-banner">
      <span class="warning-banner__icon">!</span>
      <span>
        <strong>Sistema no configurado.</strong>
        Establece el porcentaje de aprobación para que los estudiantes puedan iniciar exámenes.
      </span>
    </div>

    <!-- Success message -->
    <div v-if="successMessage" class="success-banner">
      <span class="success-banner__icon">&#10003;</span>
      {{ successMessage }}
      <button class="banner-close" @click="successMessage = null">&#10005;</button>
    </div>

    <!-- Save error -->
    <div v-if="saveError" class="error-banner">
      {{ saveError }}
      <button class="banner-close" @click="saveError = null">&#10005;</button>
    </div>

    <!-- Loading state -->
    <div v-if="isLoadingConfig" class="loading-state">
      <div class="spinner" />
      <p>Cargando configuración...</p>
    </div>

    <!-- Load error state -->
    <div v-else-if="loadError" class="error-state">
      <p>{{ loadError }}</p>
      <button class="btn btn--secondary" @click="loadConfig">Reintentar</button>
    </div>

    <!-- Config form -->
    <div v-else-if="config" class="form-card">
      <AdminConfigForm
        :initial-data="config"
        :estado-sistema="config.estado_sistema"
        :is-loading="isSaving"
        @submit="handleSave"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

interface ExamConfig {
  num_preguntas: number
  segundos_por_pregunta: number
  porcentaje_aprobacion: number | null
  updated_at: string | null
  updated_by: string | null
  estado_sistema: string
}

const auth = useAuthStore()
const runtimeConfig = useRuntimeConfig()
const apiBase = runtimeConfig.public.apiBase
const router = useRouter()

// Redirect non-admins (editors) to /admin dashboard
onMounted(() => {
  if (!auth.isAdmin) {
    navigateTo('/admin')
    return
  }
  loadConfig()
})

const config = ref<ExamConfig | null>(null)
const isLoadingConfig = ref(false)
const isSaving = ref(false)
const loadError = ref<string | null>(null)
const saveError = ref<string | null>(null)
const successMessage = ref<string | null>(null)

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function loadConfig() {
  isLoadingConfig.value = true
  loadError.value = null
  try {
    const data = await $fetch<ExamConfig>(`${apiBase}/api/admin/config`, {
      headers: getHeaders(),
    })
    config.value = data
  } catch (error: unknown) {
    let msg = 'Error al cargar la configuración'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    loadError.value = msg
  } finally {
    isLoadingConfig.value = false
  }
}

async function handleSave(formData: {
  num_preguntas: number
  segundos_por_pregunta: number
  porcentaje_aprobacion: number | null
}) {
  if (!config.value) return

  saveError.value = null
  successMessage.value = null
  isSaving.value = true

  // Build payload with only changed fields
  const payload: Record<string, unknown> = {}
  if (formData.num_preguntas !== config.value.num_preguntas) {
    payload.num_preguntas = formData.num_preguntas
  }
  if (formData.segundos_por_pregunta !== config.value.segundos_por_pregunta) {
    payload.segundos_por_pregunta = formData.segundos_por_pregunta
  }
  if (formData.porcentaje_aprobacion !== config.value.porcentaje_aprobacion) {
    payload.porcentaje_aprobacion = formData.porcentaje_aprobacion
  }

  // Always send something; if nothing changed, just refresh
  if (Object.keys(payload).length === 0) {
    successMessage.value = 'Configuración guardada'
    isSaving.value = false
    return
  }

  try {
    const updated = await $fetch<ExamConfig>(`${apiBase}/api/admin/config`, {
      method: 'PUT',
      headers: getHeaders(),
      body: payload,
    })
    config.value = updated
    successMessage.value = 'Configuración guardada'
  } catch (error: unknown) {
    let msg = 'Error al guardar la configuración'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    saveError.value = msg
  } finally {
    isSaving.value = false
  }
}

function handleCancel() {
  router.push('/admin')
}
</script>

<style scoped>
.config-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 640px;
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem;
}

/* Banners */
.warning-banner,
.success-banner,
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
}

.warning-banner {
  background: #fffbeb;
  border: 1px solid #fcd34d;
  color: #92400e;
}

.warning-banner__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: #fbbf24;
  color: white;
  font-weight: 700;
  font-size: 0.75rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.success-banner {
  background: #f0fdf4;
  border: 1px solid #86efac;
  color: #166534;
  justify-content: space-between;
}

.success-banner__icon {
  margin-right: 0.25rem;
  font-weight: 700;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  justify-content: space-between;
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

/* Loading / error states */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  text-align: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  color: #6b7280;
  font-size: 0.9375rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top-color: #1a56db;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Form card */
.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

/* Utility button (for retry) */
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
}

.btn--secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--secondary:hover {
  background: #f9fafb;
}
</style>
