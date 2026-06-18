<template>
  <div class="student-dashboard">
    <div class="dashboard-hero">
      <h1>Bienvenido, {{ auth.user?.nombre_completo?.split(' ')[0] }}</h1>
      <p>Practica para tu examen de manejo con preguntas oficiales.</p>
    </div>

    <div class="dashboard-action">
      <button
        class="btn-start-exam"
        :disabled="exam.isLoading"
        @click="handleStartExam"
      >
        {{ exam.isLoading ? 'Preparando examen...' : 'Iniciar examen' }}
      </button>
      <p v-if="examError" class="exam-error">{{ examError }}</p>
    </div>

    <div class="dashboard-history">
      <h2>Historial de exámenes</h2>

      <div v-if="isLoadingHistory" class="history-loading">
        <p>Cargando historial...</p>
      </div>

      <template v-else-if="history && history.items.length > 0">
        <div class="history-list">
          <div
            v-for="item in history.items"
            :key="item.attempt_id"
            class="history-item"
            :class="item.resultado === 'aprobado' ? 'history-item--approved' : 'history-item--failed'"
          >
            <div class="history-item__info">
              <span class="history-item__date">{{ formatDate(item.iniciado_at) }}</span>
              <span class="history-item__score">
                {{ item.puntuacion }} / {{ item.total_preguntas }}
              </span>
            </div>
            <span class="history-item__resultado">
              {{ item.resultado === 'aprobado' ? 'Aprobado' : 'Reprobado' }}
            </span>
            <NuxtLink
              :to="`/exam/${item.attempt_id}/results`"
              class="history-item__link"
            >
              Ver
            </NuxtLink>
          </div>
        </div>
      </template>

      <p v-else class="history-empty">
        Aún no has realizado ningún examen.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const auth = useAuthStore()
const exam = useExamStore()
const { startExam, fetchHistory } = useExam()

const examError = ref('')
const isLoadingHistory = ref(true)
const history = ref<{
  total: number
  page: number
  page_size: number
  items: Array<{
    attempt_id: string
    iniciado_at: string
    finalizado_at: string | null
    puntuacion: number | null
    total_preguntas: number
    resultado: string | null
  }>
} | null>(null)

onMounted(async () => {
  const result = await fetchHistory()
  history.value = result
  isLoadingHistory.value = false
})

const handleStartExam = async () => {
  examError.value = ''
  const result = await startExam()
  if (result.success && exam.attemptId) {
    navigateTo(`/exam/${exam.attemptId}`)
  } else {
    examError.value = result.error ?? 'Error al iniciar el examen'
  }
}

const formatDate = (isoDate: string) => {
  return new Date(isoDate).toLocaleDateString('es-MX', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<style scoped>
.student-dashboard {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-hero {
  text-align: center;
  padding: 2rem 1rem;
}

.dashboard-hero h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem;
}

.dashboard-hero p {
  color: #6b7280;
  margin: 0;
}

.dashboard-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.btn-start-exam {
  background: #1a56db;
  color: white;
  border: none;
  padding: 1rem 2.5rem;
  border-radius: 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-start-exam:hover:not(:disabled) {
  background: #1e429f;
}

.btn-start-exam:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.exam-error {
  color: #dc2626;
  font-size: 0.875rem;
  text-align: center;
}

.dashboard-history {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.dashboard-history h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem;
}

.history-loading,
.history-empty {
  color: #9ca3af;
  font-size: 0.875rem;
  text-align: center;
  padding: 1.5rem 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  border-left: 3px solid;
  background: #f9fafb;
}

.history-item--approved { border-left-color: #22c55e; }
.history-item--failed { border-left-color: #ef4444; }

.history-item__info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.history-item__date {
  font-size: 0.75rem;
  color: #6b7280;
}

.history-item__score {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.history-item__resultado {
  font-size: 0.75rem;
  font-weight: 600;
}

.history-item--approved .history-item__resultado { color: #15803d; }
.history-item--failed .history-item__resultado { color: #dc2626; }

.history-item__link {
  font-size: 0.75rem;
  color: #1a56db;
  text-decoration: none;
}

.history-item__link:hover {
  text-decoration: underline;
}
</style>
