<template>
  <div class="exam-page">
    <!-- Cargando -->
    <div v-if="isLoading" class="exam-loading">
      <p>Cargando examen...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="exam-error">
      <p>{{ error }}</p>
      <NuxtLink to="/dashboard">Volver al dashboard</NuxtLink>
    </div>

    <!-- Examen activo -->
    <template v-else-if="preguntaActual">
      <div class="exam-header">
        <ExamProgressBar :current="currentOrden" :total="totalPreguntas" />
        <ExamTimerBar :remaining="remaining" :total="segundosPorPregunta" />
      </div>

      <ExamQuestionCard
        :pregunta="preguntaActual"
        :selected-answer="selectedAnswer"
        :disabled="isSubmitting"
        @answer="handleAnswer"
      />

      <div class="exam-footer">
        <button
          class="btn-finish-early"
          :disabled="isSubmitting"
          @click="handleFinishEarly"
        >
          Terminar examen
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

const route = useRoute()
const examStore = useExamStore()
const { submitAnswer, finishEarly, isLoading, preguntaActual, resumen, totalPreguntas, segundosPorPregunta, currentOrden, error } = useExam()

const selectedAnswer = ref<string | null>(null)
const isSubmitting = ref(false)

// Guard de examen activo — ejecuta en SSR y cliente sin flash
if (!examStore.attemptId) {
  await navigateTo('/dashboard')
}

// Redirigir a resultados cuando el examen termina
watch(resumen, (newResumen) => {
  if (newResumen && examStore.attemptId) {
    navigateTo(`/exam/${examStore.attemptId}/results`)
  }
})

// Timer
const { remaining, start: startTimer, stop: stopTimer, reset: resetTimer } = useTimer(
  segundosPorPregunta.value,
  handleTimeout,
)

// Iniciar timer al montar (si hay pregunta activa)
onMounted(() => {
  if (preguntaActual.value) {
    resetTimer(segundosPorPregunta.value)  // Asegurar duración correcta antes de iniciar
    startTimer()
  }
})

// Reiniciar timer cuando cambia la pregunta
watch(preguntaActual, (newPregunta, oldPregunta) => {
  if (newPregunta && newPregunta.orden !== oldPregunta?.orden) {
    selectedAnswer.value = null
    resetTimer(segundosPorPregunta.value)
    startTimer()
  }
})

async function handleAnswer(letra: string) {
  if (isSubmitting.value) return
  selectedAnswer.value = letra
  isSubmitting.value = true
  stopTimer()

  const { finished } = await submitAnswer(currentOrden.value, letra, false)

  if (!finished) {
    isSubmitting.value = false
    // El watch de preguntaActual reiniciará el timer
  }
  // Si finished=true, el watch de resumen redirigirá
}

async function handleTimeout() {
  if (isSubmitting.value) return
  isSubmitting.value = true

  await submitAnswer(currentOrden.value, null, true)
  isSubmitting.value = false
}

async function handleFinishEarly() {
  if (isSubmitting.value) return
  isSubmitting.value = true
  stopTimer()
  await finishEarly()
  // el watch de resumen redirigirá
}
</script>

<style scoped>
.exam-page {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem;
}

.exam-loading,
.exam-error {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.exam-error a {
  color: #1a56db;
  text-decoration: underline;
}

.exam-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.exam-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-finish-early {
  background: transparent;
  color: #9ca3af;
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.15s;
}

.btn-finish-early:hover:not(:disabled) {
  color: #dc2626;
  border-color: #fca5a5;
  background: #fef2f2;
}

.btn-finish-early:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
