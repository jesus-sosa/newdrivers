<template>
  <div class="results-page">
    <div v-if="isLoading" class="results-loading">
      <p>Cargando resultados...</p>
    </div>

    <template v-else-if="results">
      <ResultsScoreCard :resumen="results" />

      <div class="results-actions">
        <NuxtLink to="/dashboard" class="btn-primary">
          Volver al dashboard
        </NuxtLink>
      </div>

      <div class="results-review">
        <h2>Revisión de preguntas</h2>
        <ResultsQuestionReview
          v-for="pregunta in results.preguntas"
          :key="pregunta.orden"
          :pregunta="pregunta"
        />
      </div>
    </template>

    <div v-else class="results-error">
      <p>No se pudieron cargar los resultados.</p>
      <NuxtLink to="/dashboard">Volver al dashboard</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const route = useRoute()
const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const attemptId = route.params.id as string

const isLoading = ref(true)
const results = ref<{
  attempt_id: string
  iniciado_at: string
  finalizado_at: string
  puntuacion: number
  total_preguntas: number
  porcentaje_obtenido: number
  porcentaje_aprobacion: number
  resultado: 'aprobado' | 'reprobado'
  preguntas: Array<{
    orden: number
    tema: string
    pregunta: string
    opciones: Record<string, string>
    opcion_seleccionada: string | null
    respuesta_correcta: string
    es_correcta: boolean | null
    tiempo_agotado: boolean
    fundamento_juridico: string | null
  }>
} | null>(null)

onMounted(async () => {
  try {
    results.value = await $fetch(`${apiBase}/api/exams/${attemptId}/results`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` },
    }) as typeof results.value
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.results-page {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
}

.results-loading,
.results-error {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.results-error a {
  color: #1a56db;
  text-decoration: underline;
}

.results-actions {
  display: flex;
  justify-content: center;
}

.btn-primary {
  background: #1a56db;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.15s;
}

.btn-primary:hover {
  background: #1e429f;
}

.results-review {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.results-review h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}
</style>
