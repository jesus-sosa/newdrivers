<template>
  <div class="import-form">
    <h3 class="import-title">Importar preguntas desde CSV</h3>

    <div class="import-input-row">
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
        class="file-input"
        :disabled="isLoading"
        @change="onFileChange"
      />
      <button
        class="btn btn--primary"
        :disabled="!selectedFile || isLoading"
        @click="handleUpload"
      >
        <span v-if="isLoading" class="btn-spinner" />
        {{ isLoading ? 'Importando...' : 'Subir CSV' }}
      </button>
    </div>

    <p v-if="!selectedFile" class="import-hint">
      Selecciona un archivo .csv para importar preguntas.
    </p>

    <div v-if="result" class="import-result">
      <p class="result-summary">
        <span class="result-item result-item--green">{{ result.insertadas }} insertadas</span>
        <span class="result-item result-item--blue">{{ result.actualizadas }} actualizadas</span>
        <span class="result-item" :class="result.errores.length > 0 ? 'result-item--red' : 'result-item--gray'">
          {{ result.errores.length }} errores
        </span>
      </p>

      <div v-if="result.errores.length > 0" class="error-list">
        <p class="error-list__title">Detalle de errores:</p>
        <ul>
          <li v-for="(err, i) in result.errores" :key="i" class="error-item">
            <strong>Fila {{ err.fila }}:</strong> {{ err.error }}
          </li>
        </ul>
      </div>
    </div>

    <p v-if="uploadError" class="upload-error">{{ uploadError }}</p>
  </div>
</template>

<script setup lang="ts">
interface ImportError {
  fila: number
  error: string
}

interface ImportResult {
  insertadas: number
  actualizadas: number
  errores: ImportError[]
}

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isLoading = ref(false)
const result = ref<ImportResult | null>(null)
const uploadError = ref<string | null>(null)

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedFile.value = target.files?.[0] ?? null
  result.value = null
  uploadError.value = null
}

async function handleUpload() {
  if (!selectedFile.value) return

  isLoading.value = true
  result.value = null
  uploadError.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const headers: Record<string, string> = {}
    if (auth.accessToken) {
      headers['Authorization'] = `Bearer ${auth.accessToken}`
    }

    const data = await $fetch<ImportResult>(`${apiBase}/api/questions/import`, {
      method: 'POST',
      body: formData,
      headers,
    })

    result.value = data

    // reset file input
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  } catch (error: unknown) {
    let msg = 'Error al importar el archivo'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const data = err.data as Record<string, unknown> | undefined
      if (typeof data?.detail === 'string') msg = data.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    uploadError.value = msg
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.import-form {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.import-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.import-input-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.file-input {
  font-size: 0.875rem;
  color: #374151;
  flex: 1;
  min-width: 0;
}

.import-hint {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin: 0;
}

.import-result {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.result-summary {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin: 0;
}

.result-item {
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
}

.result-item--green {
  background: #dcfce7;
  color: #166534;
}

.result-item--blue {
  background: #dbeafe;
  color: #1e40af;
}

.result-item--red {
  background: #fee2e2;
  color: #991b1b;
}

.result-item--gray {
  background: #f1f5f9;
  color: #475569;
}

.error-list {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 0.375rem;
  padding: 0.75rem;
}

.error-list__title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #9f1239;
  margin: 0 0 0.5rem;
}

.error-list ul {
  margin: 0;
  padding-left: 1.25rem;
}

.error-item {
  font-size: 0.8125rem;
  color: #881337;
  margin-bottom: 0.25rem;
}

.upload-error {
  font-size: 0.875rem;
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 0.375rem;
  padding: 0.625rem 0.875rem;
  margin: 0;
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
  white-space: nowrap;
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
