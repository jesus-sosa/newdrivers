<template>
  <div class="edit-question-page">
    <div class="page-header">
      <NuxtLink to="/admin/questions" class="back-link">&larr; Volver al listado</NuxtLink>
      <h1 class="page-heading">Editar pregunta</h1>
    </div>

    <div v-if="loadError" class="load-error">
      <p>{{ loadError }}</p>
      <button class="btn btn--secondary" @click="loadQuestion">Reintentar</button>
    </div>

    <div v-else-if="isFetching" class="loading-state">
      <div class="spinner" />
      <p>Cargando pregunta...</p>
    </div>

    <div v-else class="form-card">
      <p v-if="submitError" class="submit-error">{{ submitError }}</p>

      <AdminQuestionForm
        :initial-data="initialData"
        :is-loading="isSubmitting"
        @submit="handleSubmit"
        @cancel="navigateTo('/admin/questions')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuestionFormData } from '~/components/admin/QuestionForm.vue'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const route = useRoute()
const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const questionId = computed(() => route.params.id as string)

const initialData = ref<Partial<QuestionFormData>>({})
const isFetching = ref(true)
const loadError = ref<string | null>(null)
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function loadQuestion() {
  isFetching.value = true
  loadError.value = null

  try {
    const data = await $fetch<QuestionFormData & { id: number; activa?: boolean }>(
      `${apiBase}/api/questions/${questionId.value}`,
      { headers: getHeaders() }
    )

    initialData.value = {
      tema: data.tema,
      pregunta: data.pregunta,
      opcion_a: data.opcion_a,
      opcion_b: data.opcion_b,
      opcion_c: data.opcion_c,
      opcion_d: data.opcion_d,
      respuesta_correcta: data.respuesta_correcta,
      imagen_archivo: data.imagen_archivo ?? '',
      descripcion_imagen: data.descripcion_imagen ?? '',
      fundamento_juridico: data.fundamento_juridico ?? '',
    }
  } catch (error: unknown) {
    let msg = 'Error al cargar la pregunta'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    loadError.value = msg
  } finally {
    isFetching.value = false
  }
}

async function handleSubmit(data: QuestionFormData) {
  isSubmitting.value = true
  submitError.value = null

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...getHeaders(),
    }

    await $fetch(`${apiBase}/api/questions/${questionId.value}`, {
      method: 'PUT',
      body: data,
      headers,
    })

    await navigateTo('/admin/questions')
  } catch (error: unknown) {
    let msg = 'Error al actualizar la pregunta'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const status = err.status as number | undefined
      const d = err.data as Record<string, unknown> | undefined
      if (status === 409) {
        msg = (typeof d?.detail === 'string' ? d.detail : 'Conflicto: la pregunta fue modificada por otro usuario.')
      } else if (typeof d?.detail === 'string') {
        msg = d.detail
      } else if (typeof err.message === 'string') {
        msg = err.message
      }
    }
    submitError.value = msg
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadQuestion()
})
</script>

<style scoped>
.edit-question-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 800px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.back-link {
  font-size: 0.875rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.15s;
}

.back-link:hover {
  color: #1a56db;
}

.page-heading {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submit-error {
  font-size: 0.875rem;
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 0.375rem;
  padding: 0.625rem 0.875rem;
  margin: 0;
}

.load-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  color: #dc2626;
  font-size: 0.9375rem;
  text-align: center;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
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

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  transition: all 0.15s;
}

.btn--secondary:hover {
  background: #f9fafb;
}
</style>
