<template>
  <div class="student-detail-page">
    <!-- Back link -->
    <NuxtLink to="/admin/usuarios" class="back-link">
      &larr; Volver a estudiantes
    </NuxtLink>

    <!-- Loading state -->
    <div v-if="isLoading" class="state-box">
      Cargando datos del estudiante...
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="state-box state-box--error">
      Estudiante no encontrado.
    </div>

    <!-- Error banner -->
    <div v-else-if="loadError" class="error-banner">
      {{ loadError }}
      <button class="banner-close" @click="loadError = null">&#10005;</button>
    </div>

    <!-- Content -->
    <template v-else-if="student">
      <!-- Student info card -->
      <div class="info-card">
        <div class="info-card__header">
          <div>
            <h1 class="info-card__name">{{ student.nombre_completo }}</h1>
            <p class="info-card__email">{{ student.email }}</p>
          </div>
          <span
            class="badge"
            :class="student.activo ? 'badge--green' : 'badge--red'"
          >
            {{ student.activo ? 'Activo' : 'Inactivo' }}
          </span>
        </div>
      </div>

      <!-- Attempts table -->
      <div class="attempts-card">
        <h2 class="attempts-card__title">Intentos de examen</h2>

        <!-- Empty state -->
        <div v-if="student.intentos.length === 0" class="state-box">
          Este estudiante no tiene intentos de examen.
        </div>

        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Puntuación</th>
                <th>Resultado</th>
                <th>Ver detalle</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attempt in student.intentos" :key="attempt.attempt_id">
                <td>{{ formatDate(attempt.iniciado_at) }}</td>
                <td>{{ attempt.puntuacion }} / {{ attempt.total_preguntas }}</td>
                <td>
                  <span
                    v-if="attempt.resultado"
                    class="badge"
                    :class="attempt.resultado === 'aprobado' ? 'badge--green' : 'badge--red'"
                  >
                    {{ attempt.resultado === 'aprobado' ? 'Aprobado' : 'Reprobado' }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <NuxtLink
                    :to="`/exam/${attempt.attempt_id}/results`"
                    class="action-link"
                  >
                    Ver detalle
                  </NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

interface AttemptItem {
  attempt_id: string
  iniciado_at: string
  finalizado_at: string | null
  puntuacion: number
  total_preguntas: number
  resultado: string | null
}

interface StudentDetail {
  id: string
  nombre_completo: string
  email: string
  activo: boolean
  created_at: string
  intentos: AttemptItem[]
}

const auth = useAuthStore()
const runtimeConfig = useRuntimeConfig()
const apiBase = runtimeConfig.public.apiBase
const route = useRoute()

const studentId = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id

const student = ref<StudentDetail | null>(null)
const isLoading = ref(false)
const loadError = ref<string | null>(null)
const notFound = ref(false)

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

async function loadStudent() {
  isLoading.value = true
  loadError.value = null
  notFound.value = false

  try {
    const data = await $fetch<StudentDetail>(
      `${apiBase}/api/admin/students/${studentId}`,
      { headers: getHeaders() }
    )
    student.value = data
  } catch (error: unknown) {
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const status = err.status as number | undefined
      if (status === 404) {
        notFound.value = true
        return
      }
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') {
        loadError.value = d.detail
      } else if (typeof err.message === 'string') {
        loadError.value = err.message
      } else {
        loadError.value = 'Error al cargar los datos del estudiante'
      }
    } else {
      loadError.value = 'Error al cargar los datos del estudiante'
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (!auth.isAdmin) {
    await navigateTo('/admin')
    return
  }
  await loadStudent()
})
</script>

<style scoped>
.student-detail-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 900px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #2563eb;
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

.state-box {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.state-box--error {
  color: #dc2626;
  border-color: #fecaca;
  background: #fef2f2;
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

.info-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.info-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.info-card__name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.25rem;
}

.info-card__email {
  font-size: 0.9375rem;
  color: #6b7280;
  margin: 0;
}

.attempts-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attempts-card__title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.data-table th,
.data-table td {
  padding: 0.625rem 0.875rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.badge--green {
  background: #d1fae5;
  color: #065f46;
}

.badge--red {
  background: #fee2e2;
  color: #991b1b;
}

.text-muted {
  color: #9ca3af;
}

.action-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.action-link:hover {
  text-decoration: underline;
}
</style>
