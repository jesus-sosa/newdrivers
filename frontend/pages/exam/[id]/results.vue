<template>
  <div class="results-page">
    <div v-if="isLoading" class="results-loading">
      <p>Cargando resultados...</p>
    </div>

    <template v-else-if="results">
      <ResultsScoreCard :resumen="results" />

      <div class="results-actions">
        <NuxtLink :to="backLink" class="btn-primary">
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
      <NuxtLink :to="backLink">Volver al dashboard</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const route = useRoute()
const { fetchResults } = useExam()
const auth = useAuthStore()

const attemptId = route.params.id as string
const backLink = computed(() => auth.user?.rol === 'admin' || auth.user?.rol === 'editor' ? '/admin' : '/dashboard')

const isLoading = ref(true)
const results = ref<Awaited<ReturnType<typeof fetchResults>>>(null)

onMounted(async () => {
  results.value = await fetchResults(attemptId)
  isLoading.value = false
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
