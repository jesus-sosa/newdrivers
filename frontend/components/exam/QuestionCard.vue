<template>
  <div class="question-card">
    <div v-if="pregunta.imagen_archivo" class="question-card__image">
      <img
        :src="`${apiBase}/static/${pregunta.imagen_archivo}`"
        :alt="pregunta.descripcion_imagen || 'Imagen de la pregunta'"
        loading="lazy"
      />
    </div>

    <div class="question-card__body">
      <p class="question-card__tema">{{ pregunta.tema }}</p>
      <p class="question-card__texto">{{ pregunta.pregunta }}</p>

      <div class="question-card__opciones">
        <ExamAnswerOption
          v-for="(texto, letra) in pregunta.opciones"
          :key="letra"
          :letter="letra"
          :text="texto"
          :selected="selectedAnswer === letra"
          :disabled="disabled"
          @select="onSelect"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  pregunta: {
    orden: number
    id: number
    tema: string
    pregunta: string
    imagen_archivo: string | null
    descripcion_imagen: string | null
    opciones: Record<string, string>
  }
  selectedAnswer: string | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  answer: [letter: string]
}>()

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const onSelect = (letter: string) => {
  if (!props.disabled) {
    emit('answer', letter)
  }
}
</script>

<style scoped>
.question-card {
  background: white;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.question-card__image {
  background: #f9fafb;
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.question-card__image img {
  max-height: 200px;
  object-fit: contain;
  border-radius: 0.375rem;
}

.question-card__body {
  padding: 1.5rem;
}

.question-card__tema {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1a56db;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem;
}

.question-card__texto {
  font-size: 1rem;
  font-weight: 500;
  color: #111827;
  line-height: 1.5;
  margin: 0 0 1.5rem;
}

.question-card__opciones {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
</style>
