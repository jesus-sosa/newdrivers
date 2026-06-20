<template>
  <div class="questions-page">
    <h1 class="page-title">Banco de Preguntas</h1>

    <!-- Top actions -->
    <div class="actions-bar">
      <div class="actions-bar__left">
        <NuxtLink to="/admin/questions/new" class="btn btn--primary">
          + Nueva pregunta
        </NuxtLink>
        <button class="btn btn--secondary" @click="showImport = !showImport">
          {{ showImport ? 'Ocultar importar' : 'Importar CSV' }}
        </button>
      </div>
    </div>

    <!-- Import form -->
    <div v-if="showImport" class="import-section">
      <ImportForm />
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <select v-model="filters.tema" class="filter-select" @change="applyFilters">
        <option value="">Todos los temas</option>
        <option v-for="t in temas" :key="t" :value="t">{{ t }}</option>
      </select>

      <input
        v-model="filters.search"
        type="text"
        class="filter-input"
        placeholder="Buscar pregunta..."
        @input="onSearchInput"
      />

      <div class="filter-toggle">
        <button
          class="toggle-btn"
          :class="{ 'toggle-btn--active': filters.activa === '' }"
          @click="setActivaFilter('')"
        >
          Todas
        </button>
        <button
          class="toggle-btn"
          :class="{ 'toggle-btn--active': filters.activa === 'true' }"
          @click="setActivaFilter('true')"
        >
          Activas
        </button>
        <button
          class="toggle-btn"
          :class="{ 'toggle-btn--active': filters.activa === 'false' }"
          @click="setActivaFilter('false')"
        >
          Inactivas
        </button>
      </div>
    </div>

    <!-- Delete error -->
    <div v-if="deleteError" class="error-banner">
      {{ deleteError }}
      <button class="error-banner__close" @click="deleteError = null">✕</button>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner" />
      <p>Cargando preguntas...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="loadError" class="error-state">
      <p>{{ loadError }}</p>
      <button class="btn btn--secondary" @click="loadQuestions">Reintentar</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="questions.length === 0" class="empty-state">
      <p>No se encontraron preguntas con los filtros aplicados.</p>
    </div>

    <!-- Table -->
    <div v-else class="table-wrapper">
      <table class="questions-table">
        <thead>
          <tr>
            <th class="col-id">ID</th>
            <th class="col-tema">Tema</th>
            <th class="col-pregunta">Pregunta</th>
            <th class="col-estado">Estado</th>
            <th class="col-acciones">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="q in questions" :key="q.id">
            <tr>
              <td class="col-id">{{ q.id }}</td>
              <td class="col-tema">{{ q.tema }}</td>
              <td class="col-pregunta">{{ truncate(q.pregunta, 60) }}</td>
              <td class="col-estado">
                <span class="badge" :class="q.activa ? 'badge--green' : 'badge--gray'">
                  {{ q.activa ? 'Activa' : 'Inactiva' }}
                </span>
              </td>
              <td class="col-acciones">
                <div class="row-actions">
                  <NuxtLink :to="`/admin/questions/${q.id}/edit`" class="action-link">
                    Editar
                  </NuxtLink>

                  <template v-if="confirmDeleteId === q.id">
                    <span class="confirm-text">¿Eliminar?</span>
                    <button class="action-btn action-btn--danger" @click="deleteQuestion(q.id)">
                      Sí
                    </button>
                    <button class="action-btn" @click="confirmDeleteId = null">
                      No
                    </button>
                  </template>
                  <button
                    v-else
                    class="action-btn action-btn--danger"
                    @click="confirmDeleteId = q.id"
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="total > 0" class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)"
      >
        &larr; Anterior
      </button>

      <span class="page-info">
        Página {{ currentPage }} de {{ totalPages }} &nbsp;&bull;&nbsp; {{ total }} pregunta{{ total !== 1 ? 's' : '' }}
      </span>

      <button
        class="page-btn"
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)"
      >
        Siguiente &rarr;
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

interface Question {
  id: number
  tema: string
  pregunta: string
  activa: boolean
}

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const PAGE_SIZE = 20

const questions = ref<Question[]>([])
const temas = ref<string[]>([])
const total = ref(0)
const currentPage = ref(1)
const isLoading = ref(false)
const loadError = ref<string | null>(null)
const confirmDeleteId = ref<number | null>(null)
const deleteError = ref<string | null>(null)
const showImport = ref(false)

const filters = reactive({
  tema: '',
  search: '',
  activa: '',
})

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

function truncate(text: string, length: number): string {
  return text.length > length ? text.slice(0, length) + '...' : text
}

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function loadQuestions() {
  isLoading.value = true
  loadError.value = null

  try {
    const params: Record<string, string> = {
      page: String(currentPage.value),
      page_size: String(PAGE_SIZE),
    }
    if (filters.tema) params.tema = filters.tema
    if (filters.search) params.search = filters.search
    if (filters.activa !== '') params.activa = filters.activa

    const query = new URLSearchParams(params).toString()

    const data = await $fetch<{
      total: number
      page: number
      page_size: number
      items: Question[]
      temas_disponibles?: string[]
    }>(`${apiBase}/api/questions?${query}`, { headers: getHeaders() })

    questions.value = data.items
    total.value = data.total
    if (data.temas_disponibles) {
      temas.value = data.temas_disponibles
    }
  } catch (error: unknown) {
    let msg = 'Error al cargar las preguntas'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    loadError.value = msg
  } finally {
    isLoading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  loadQuestions()
}

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(applyFilters, 350)
}

function setActivaFilter(value: string) {
  filters.activa = value
  applyFilters()
}

function goToPage(page: number) {
  currentPage.value = page
  loadQuestions()
}

async function deleteQuestion(id: number) {
  deleteError.value = null
  try {
    await $fetch(`${apiBase}/api/questions/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    })
    await loadQuestions()
  } catch (error: unknown) {
    let msg = 'Error al eliminar la pregunta'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    deleteError.value = msg
  } finally {
    confirmDeleteId.value = null
  }
}

onMounted(() => {
  loadQuestions()
})

onUnmounted(() => {
  if (searchTimeout) clearTimeout(searchTimeout)
})
</script>

<style scoped>
.questions-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.error-banner__close {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  font-size: 1rem;
  padding: 0 0.25rem;
}

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions-bar__left {
  display: flex;
  gap: 0.75rem;
}

.import-section {
  margin-bottom: 0.25rem;
}

.filter-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.875rem 1rem;
}

.filter-select,
.filter-input {
  padding: 0.4375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #111827;
  background: white;
}

.filter-select {
  min-width: 180px;
}

.filter-input {
  flex: 1;
  min-width: 160px;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #1a56db;
}

.filter-toggle {
  display: flex;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  overflow: hidden;
}

.toggle-btn {
  padding: 0.4375rem 0.875rem;
  font-size: 0.8125rem;
  background: white;
  color: #6b7280;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  border-right: 1px solid #d1d5db;
}

.toggle-btn:last-child {
  border-right: none;
}

.toggle-btn:hover {
  background: #f9fafb;
  color: #111827;
}

.toggle-btn--active {
  background: #1a56db;
  color: white;
}

.toggle-btn--active:hover {
  background: #1e429f;
  color: white;
}

/* States */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  text-align: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  color: #6b7280;
  font-size: 0.9375rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top-color: #1a56db;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.questions-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.questions-table th {
  text-align: left;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.questions-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
  vertical-align: middle;
}

.questions-table tr:last-child td {
  border-bottom: none;
}

.questions-table tr:hover td {
  background: #f9fafb;
}

.col-id { width: 60px; }
.col-tema { width: 160px; }
.col-pregunta { }
.col-estado { width: 100px; }
.col-acciones { width: 200px; }

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

.badge--gray {
  background: #f1f5f9;
  color: #475569;
}

/* Row actions */
.row-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-link {
  font-size: 0.8125rem;
  color: #1a56db;
  text-decoration: none;
  font-weight: 500;
}

.action-link:hover {
  text-decoration: underline;
}

.confirm-text {
  font-size: 0.8125rem;
  color: #374151;
}

.action-btn {
  font-size: 0.8125rem;
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #f9fafb;
}

.action-btn--danger {
  color: #dc2626;
  border-color: #fca5a5;
}

.action-btn--danger:hover {
  background: #fee2e2;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.5rem 0;
}

.page-btn {
  padding: 0.4375rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s;
}

.page-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: all 0.15s;
}

.btn--primary {
  background: #1a56db;
  color: white;
}

.btn--primary:hover {
  background: #1e429f;
}

.btn--secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn--secondary:hover {
  background: #f9fafb;
}
</style>
