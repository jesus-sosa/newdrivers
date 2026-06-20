<template>
  <form class="config-form" @submit.prevent="handleSubmit">
    <!-- System state badge -->
    <div class="form-section">
      <div class="state-row">
        <span class="state-label">Estado del sistema:</span>
        <span
          class="badge"
          :class="estadoSistema === 'activo' ? 'badge--green' : 'badge--warning'"
        >
          {{ estadoSistema === 'activo' ? 'Activo' : 'No configurado' }}
        </span>
      </div>
      <p v-if="estadoSistema === 'no_configurado'" class="state-hint">
        El sistema no está configurado. Establece el porcentaje de aprobación para activarlo.
      </p>
    </div>

    <!-- num_preguntas -->
    <div class="form-group">
      <label class="form-label" for="num_preguntas">
        Número de preguntas por examen
      </label>
      <input
        id="num_preguntas"
        v-model.number="form.num_preguntas"
        type="number"
        class="form-input"
        min="1"
        step="1"
        placeholder="Ej: 20"
        required
      />
      <span class="form-hint">Mínimo 1. Debe haber al menos este número de preguntas activas en el banco.</span>
    </div>

    <!-- segundos_por_pregunta -->
    <div class="form-group">
      <label class="form-label" for="segundos_por_pregunta">
        Segundos por pregunta
      </label>
      <input
        id="segundos_por_pregunta"
        v-model.number="form.segundos_por_pregunta"
        type="number"
        class="form-input"
        min="10"
        step="1"
        placeholder="Ej: 60"
        required
      />
      <span class="form-hint">Mínimo 10 segundos por pregunta.</span>
    </div>

    <!-- porcentaje_aprobacion -->
    <div class="form-group">
      <label class="form-label" for="porcentaje_aprobacion">
        Porcentaje de aprobación (%)
      </label>
      <input
        id="porcentaje_aprobacion"
        v-model="porcentajeInput"
        type="number"
        class="form-input"
        min="0"
        max="100"
        step="0.1"
        placeholder="Ej: 70 (dejar vacío para desactivar)"
      />
      <span class="form-hint">Entre 0 y 100. Déjalo vacío para marcar el sistema como no configurado.</span>
    </div>

    <div class="form-actions">
      <button
        type="button"
        class="btn btn--secondary"
        @click="$emit('cancel')"
      >
        Cancelar
      </button>
      <button
        type="submit"
        class="btn btn--primary"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="btn-spinner" />
        {{ isLoading ? 'Guardando...' : 'Guardar configuración' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
export interface ConfigFormData {
  num_preguntas: number
  segundos_por_pregunta: number
  porcentaje_aprobacion: number | null
}

const props = withDefaults(defineProps<{
  initialData?: Partial<ConfigFormData>
  estadoSistema?: string
  isLoading?: boolean
}>(), {
  estadoSistema: 'no_configurado',
  isLoading: false,
})

const emit = defineEmits<{
  (e: 'submit', data: ConfigFormData): void
  (e: 'cancel'): void
}>()

const form = reactive<ConfigFormData>({
  num_preguntas: props.initialData?.num_preguntas ?? 20,
  segundos_por_pregunta: props.initialData?.segundos_por_pregunta ?? 60,
  porcentaje_aprobacion: props.initialData?.porcentaje_aprobacion ?? null,
})

// Vue 3 automatically converts <input type="number"> values to numbers via looseToNumber,
// so this ref holds either a number (valid input) or '' (empty field).
const porcentajeInput = ref<number | string>(
  props.initialData?.porcentaje_aprobacion ?? ''
)

watch(porcentajeInput, (val) => {
  if (val === '' || val == null) {
    form.porcentaje_aprobacion = null
  } else {
    const num = typeof val === 'number' ? val : parseFloat(String(val).trim())
    form.porcentaje_aprobacion = Number.isFinite(num) ? num : null
  }
})

watch(
  () => props.initialData,
  (data) => {
    if (!data) return
    form.num_preguntas = data.num_preguntas ?? 20
    form.segundos_por_pregunta = data.segundos_por_pregunta ?? 60
    form.porcentaje_aprobacion = data.porcentaje_aprobacion ?? null
    porcentajeInput.value = data.porcentaje_aprobacion ?? ''
  },
  { deep: true }
)

function handleSubmit() {
  emit('submit', { ...form })
}
</script>

<style scoped>
.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-section {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.state-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.state-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.state-hint {
  font-size: 0.8125rem;
  color: #92400e;
  margin: 0;
}

/* Badge */
.badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge--green {
  background: #dcfce7;
  color: #166534;
}

.badge--warning {
  background: #fef3c7;
  color: #92400e;
}

/* Form */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
  color: #111827;
  background: white;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}

.form-input:focus {
  outline: none;
  border-color: #1a56db;
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
}

.form-hint {
  font-size: 0.8125rem;
  color: #6b7280;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 0.25rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}

.btn--primary {
  background: #1a56db;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background: #1e429f;
}

.btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--secondary:hover {
  background: #f9fafb;
}

.btn-spinner {
  display: inline-block;
  width: 0.875rem;
  height: 0.875rem;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
