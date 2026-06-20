<template>
  <div class="history-page">
    <h1 class="page-title">Mis intentos de examen</h1>

    <!-- Error banner -->
    <div v-if="loadError" class="error-banner">
      {{ loadError }}
      <button class="banner-close" @click="loadError = null">&#10005;</button>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="history-page__loading">
      Cargando historial...
    </div>

    <!-- Empty state -->
    <div v-else-if="items.length === 0 && !loadError" class="history-page__empty">
      No tienes intentos de examen todavía.
    </div>

    <!-- List -->
    <div v-else class="history-page__list">
      <ResultsHistoryCard
        v-for="item in items"
        :key="item.attempt_id"
        :attempt-id="item.attempt_id"
        :iniciado-at="item.iniciado_at"
        :finalizado-at="item.finalizado_at"
        :puntuacion="item.puntuacion"
        :total-preguntas="item.total_preguntas"
        :resultado="item.resultado"
      />
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination">
      <button
        class="btn btn--secondary"
        :disabled="page === 1"
        @click="goToPage(page - 1)"
      >
        Anterior
      </button>
      <span class="pagination__info">Página {{ page }} de {{ totalPages }}</span>
      <button
        class="btn btn--secondary"
        :disabled="page >= totalPages"
        @click="goToPage(page + 1)"
      >
        Siguiente
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['auth'],
})

interface HistoryItem {
  attempt_id: string
  iniciado_at: string
  finalizado_at: string | null
  puntuacion: number
  total_preguntas: number
  resultado: string | null
}

interface HistoryResponse {
  total: number
  page: number
  page_size: number
  items: HistoryItem[]
}

const auth = useAuthStore()
const runtimeConfig = useRuntimeConfig()
const apiBase = runtimeConfig.public.apiBase

const items = ref<HistoryItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const isLoading = ref(false)
const loadError = ref<string | null>(null)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function loadHistory() {
  isLoading.value = true
  loadError.value = null

  try {
    const data = await $fetch<HistoryResponse>(
      `${apiBase}/api/exams/history?page=${page.value}&page_size=${pageSize}`,
      { headers: getHeaders() }
    )
    items.value = data.items
    total.value = data.total
  } catch (error: unknown) {
    let msg = 'Error al cargar el historial'
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

function goToPage(newPage: number) {
  page.value = newPage
  loadHistory()
}

onMounted(() => {
  page.value = 1
  loadHistory()
})
</script>

<style scoped>
.history-page {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1rem;
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.history-page__loading,
.history-page__empty {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.history-page__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding-top: 0.5rem;
}

.pagination__info {
  font-size: 0.9375rem;
  color: #6b7280;
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.banner-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: inherit;
  opacity: 0.7;
  padding: 0 0.25rem;
  flex-shrink: 0;
}

.banner-close:hover {
  opacity: 1;
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

.btn--secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
