<template>
  <form class="question-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label class="form-label" for="tema">Tema</label>
      <input
        id="tema"
        v-model="form.tema"
        type="text"
        class="form-input"
        list="temas-list"
        placeholder="Seleccionar o escribir tema..."
        required
      />
      <datalist id="temas-list">
        <option v-for="t in temas" :key="t" :value="t" />
      </datalist>
    </div>

    <div class="form-group">
      <label class="form-label" for="pregunta">Pregunta</label>
      <textarea
        id="pregunta"
        v-model="form.pregunta"
        class="form-textarea"
        rows="3"
        placeholder="Texto de la pregunta..."
        required
      />
    </div>

    <div class="form-row">
      <div class="form-group form-group--half">
        <label class="form-label" for="opcion_a">Opción A</label>
        <input
          id="opcion_a"
          v-model="form.opcion_a"
          type="text"
          class="form-input"
          placeholder="Opción A"
          required
        />
      </div>
      <div class="form-group form-group--half">
        <label class="form-label" for="opcion_b">Opción B</label>
        <input
          id="opcion_b"
          v-model="form.opcion_b"
          type="text"
          class="form-input"
          placeholder="Opción B"
          required
        />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group form-group--half">
        <label class="form-label" for="opcion_c">Opción C</label>
        <input
          id="opcion_c"
          v-model="form.opcion_c"
          type="text"
          class="form-input"
          placeholder="Opción C"
          required
        />
      </div>
      <div class="form-group form-group--half">
        <label class="form-label" for="opcion_d">Opción D</label>
        <input
          id="opcion_d"
          v-model="form.opcion_d"
          type="text"
          class="form-input"
          placeholder="Opción D"
          required
        />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">Respuesta correcta</label>
      <div class="radio-group">
        <label v-for="opt in ['A', 'B', 'C', 'D']" :key="opt" class="radio-label">
          <input
            v-model="form.respuesta_correcta"
            type="radio"
            :value="opt"
            class="radio-input"
            required
          />
          <span class="radio-text">{{ opt }}</span>
        </label>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="imagen_archivo">Imagen (archivo, opcional)</label>
      <input
        id="imagen_archivo"
        v-model="form.imagen_archivo"
        type="text"
        class="form-input"
        placeholder="Nombre del archivo de imagen..."
      />
    </div>

    <div class="form-group">
      <label class="form-label" for="descripcion_imagen">Descripción de imagen (opcional)</label>
      <input
        id="descripcion_imagen"
        v-model="form.descripcion_imagen"
        type="text"
        class="form-input"
        placeholder="Descripción accesible de la imagen..."
      />
    </div>

    <div class="form-group">
      <label class="form-label" for="fundamento_juridico">Fundamento jurídico (opcional)</label>
      <textarea
        id="fundamento_juridico"
        v-model="form.fundamento_juridico"
        class="form-textarea"
        rows="2"
        placeholder="Artículo o norma relacionada..."
      />
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
        {{ isLoading ? 'Guardando...' : 'Guardar' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
export interface QuestionFormData {
  tema: string
  pregunta: string
  opcion_a: string
  opcion_b: string
  opcion_c: string
  opcion_d: string
  respuesta_correcta: string
  imagen_archivo?: string
  descripcion_imagen?: string
  fundamento_juridico?: string
}

const props = withDefaults(defineProps<{
  initialData?: Partial<QuestionFormData>
  isLoading?: boolean
}>(), {
  isLoading: false,
})

const emit = defineEmits<{
  (e: 'submit', data: QuestionFormData): void
  (e: 'cancel'): void
}>()

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const temas = ref<string[]>([])

const form = reactive<QuestionFormData>({
  tema: props.initialData?.tema ?? '',
  pregunta: props.initialData?.pregunta ?? '',
  opcion_a: props.initialData?.opcion_a ?? '',
  opcion_b: props.initialData?.opcion_b ?? '',
  opcion_c: props.initialData?.opcion_c ?? '',
  opcion_d: props.initialData?.opcion_d ?? '',
  respuesta_correcta: props.initialData?.respuesta_correcta ?? '',
  imagen_archivo: props.initialData?.imagen_archivo ?? '',
  descripcion_imagen: props.initialData?.descripcion_imagen ?? '',
  fundamento_juridico: props.initialData?.fundamento_juridico ?? '',
})

watch(
  () => props.initialData,
  (data) => {
    if (!data) return
    Object.assign(form, {
      tema: data.tema ?? '',
      pregunta: data.pregunta ?? '',
      opcion_a: data.opcion_a ?? '',
      opcion_b: data.opcion_b ?? '',
      opcion_c: data.opcion_c ?? '',
      opcion_d: data.opcion_d ?? '',
      respuesta_correcta: data.respuesta_correcta ?? '',
      imagen_archivo: data.imagen_archivo ?? '',
      descripcion_imagen: data.descripcion_imagen ?? '',
      fundamento_juridico: data.fundamento_juridico ?? '',
    })
  },
  { deep: true }
)

onMounted(async () => {
  try {
    const headers = auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
    const data = await $fetch<{ temas: string[] }>(`${apiBase}/api/questions/temas`, { headers })
    temas.value = data.temas
  } catch {
    // silently ignore — datalist will simply be empty
  }
})

function handleSubmit() {
  emit('submit', { ...form })
}
</script>

<style scoped>
.question-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  flex: 1;
}

.form-group--half {
  flex: 1;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-textarea {
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

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #1a56db;
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.radio-group {
  display: flex;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #374151;
}

.radio-input {
  accent-color: #1a56db;
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.radio-text {
  font-weight: 600;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 0.5rem;
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
