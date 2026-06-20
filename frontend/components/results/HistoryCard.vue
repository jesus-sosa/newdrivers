<template>
  <div class="history-card">
    <div class="history-card__body">
      <div class="history-card__meta">
        <span class="history-card__date">{{ formattedDate }}</span>
        <span
          v-if="resultado"
          class="badge"
          :class="resultado === 'aprobado' ? 'badge--green' : 'badge--red'"
        >
          {{ resultado === 'aprobado' ? 'Aprobado' : 'Reprobado' }}
        </span>
        <span v-else class="text-muted">—</span>
      </div>

      <div class="history-card__score">
        <span class="history-card__score-label">Puntuación</span>
        <span class="history-card__score-value">{{ puntuacion }} / {{ totalPreguntas }}</span>
      </div>
    </div>

    <div class="history-card__actions">
      <NuxtLink :to="`/exam/${attemptId}/results`" class="btn btn--secondary btn--sm">
        Ver detalle
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  attemptId: string
  iniciadoAt: string
  finalizadoAt: string | null
  puntuacion: number
  totalPreguntas: number
  resultado: string | null
}

const props = defineProps<Props>()

const formattedDate = computed(() => {
  const date = new Date(props.iniciadoAt)
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})
</script>

<style scoped>
.history-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.history-card:hover {
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.06);
  border-color: #d1d5db;
}

.history-card__body {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.history-card__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.history-card__date {
  font-size: 0.9375rem;
  color: #374151;
  font-weight: 500;
}

.history-card__score {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.history-card__score-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #9ca3af;
  font-weight: 500;
}

.history-card__score-value {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}

.history-card__actions {
  flex-shrink: 0;
}

.badge {
  display: inline-block;
  padding: 0.125rem 0.625rem;
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

.btn--secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--secondary:hover {
  background: #f9fafb;
}

.btn--sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}
</style>
