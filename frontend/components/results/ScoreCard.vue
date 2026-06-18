<template>
  <div class="score-card" :class="resultClass">
    <div class="score-card__badge">
      {{ resumen.resultado === 'aprobado' ? '✓' : '✗' }}
    </div>
    <div class="score-card__main">
      <p class="score-card__resultado">
        {{ resumen.resultado === 'aprobado' ? 'Aprobado' : 'Reprobado' }}
      </p>
      <p class="score-card__score">
        {{ resumen.puntuacion }} / {{ resumen.total_preguntas }}
        <span class="score-card__pct">{{ resumen.porcentaje_obtenido }}%</span>
      </p>
    </div>
    <div class="score-card__meta">
      <span>Mínimo para aprobar: {{ resumen.porcentaje_aprobacion }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  resumen: {
    attempt_id: string
    puntuacion: number
    total_preguntas: number
    porcentaje_obtenido: number
    porcentaje_aprobacion: number
    resultado: 'aprobado' | 'reprobado'
  }
}>()

const resultClass = computed(() =>
  props.resumen.resultado === 'aprobado' ? 'score-card--approved' : 'score-card--failed'
)
</script>

<style scoped>
.score-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 2px solid;
}

.score-card--approved {
  background: #f0fdf4;
  border-color: #86efac;
  color: #15803d;
}

.score-card--failed {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #dc2626;
}

.score-card__badge {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  font-weight: 700;
  flex-shrink: 0;
  background: currentColor;
  color: white;
}

.score-card--approved .score-card__badge { background: #22c55e; }
.score-card--failed .score-card__badge { background: #ef4444; }

.score-card__main {
  flex: 1;
}

.score-card__resultado {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.score-card__score {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #111827;
}

.score-card__pct {
  font-size: 1rem;
  color: #6b7280;
  margin-left: 0.5rem;
}

.score-card__meta {
  font-size: 0.875rem;
  opacity: 0.8;
}
</style>
