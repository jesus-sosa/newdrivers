<template>
  <div class="question-review" :class="reviewClass">
    <div class="question-review__header">
      <span class="question-review__orden">{{ pregunta.orden }}</span>
      <span class="question-review__tema">{{ pregunta.tema }}</span>
      <span class="question-review__status">
        {{ statusText }}
      </span>
    </div>

    <p class="question-review__texto">{{ pregunta.pregunta }}</p>

    <div class="question-review__opciones">
      <div
        v-for="(texto, letra) in pregunta.opciones"
        :key="letra"
        class="review-opcion"
        :class="{
          'review-opcion--selected': pregunta.opcion_seleccionada === letra,
          'review-opcion--correct': pregunta.respuesta_correcta === letra,
        }"
      >
        <span class="review-opcion__letter">{{ letra }}</span>
        <span class="review-opcion__text">{{ texto }}</span>
        <span v-if="pregunta.respuesta_correcta === letra" class="review-opcion__tag">✓ Correcta</span>
        <span v-else-if="pregunta.opcion_seleccionada === letra && !pregunta.es_correcta" class="review-opcion__tag">✗ Tu respuesta</span>
      </div>
    </div>

    <ResultsLegalBasisBlock :fundamento="pregunta.fundamento_juridico" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  pregunta: {
    orden: number
    tema: string
    pregunta: string
    opciones: Record<string, string>
    opcion_seleccionada: string | null
    respuesta_correcta: string
    es_correcta: boolean | null
    tiempo_agotado: boolean
    fundamento_juridico: string | null
  }
}>()

const reviewClass = computed(() => {
  if (props.pregunta.tiempo_agotado) return 'question-review--timeout'
  return props.pregunta.es_correcta ? 'question-review--correct' : 'question-review--wrong'
})

const statusText = computed(() => {
  if (props.pregunta.tiempo_agotado) return 'Sin respuesta (tiempo agotado)'
  return props.pregunta.es_correcta ? 'Correcta' : 'Incorrecta'
})
</script>

<style scoped>
.question-review {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  border-left-width: 4px;
}

.question-review--correct { border-left-color: #22c55e; }
.question-review--wrong { border-left-color: #ef4444; }
.question-review--timeout { border-left-color: #f59e0b; }

.question-review__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.question-review__orden {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  color: #374151;
  flex-shrink: 0;
}

.question-review__tema {
  font-size: 0.75rem;
  color: #6b7280;
  flex: 1;
}

.question-review__status {
  font-size: 0.75rem;
  font-weight: 600;
}

.question-review--correct .question-review__status { color: #15803d; }
.question-review--wrong .question-review__status { color: #dc2626; }
.question-review--timeout .question-review__status { color: #d97706; }

.question-review__texto {
  font-size: 0.9375rem;
  color: #111827;
  margin: 0 0 1rem;
  line-height: 1.5;
}

.question-review__opciones {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.review-opcion {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  background: #f9fafb;
  font-size: 0.875rem;
}

.review-opcion--correct {
  background: #f0fdf4;
  color: #15803d;
}

.review-opcion--selected:not(.review-opcion--correct) {
  background: #fef2f2;
  color: #dc2626;
}

.review-opcion__letter {
  font-weight: 700;
  min-width: 20px;
}

.review-opcion__text {
  flex: 1;
}

.review-opcion__tag {
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: auto;
}
</style>
