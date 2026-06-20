<template>
  <div class="students-page">
    <div class="students-page__header">
      <h1 class="page-title">Gestión de Estudiantes</h1>
      <NuxtLink to="/admin/usuarios/new" class="btn btn--primary">
        Agregar estudiante
      </NuxtLink>
    </div>

    <!-- Success banner -->
    <div v-if="route.query.created === '1'" class="success-banner">
      El estudiante fue creado correctamente.
      <button class="banner-close" @click="clearCreatedParam">&#10005;</button>
    </div>

    <!-- Filters bar -->
    <div class="students-page__filters">
      <input
        v-model="searchInput"
        type="text"
        class="form-input form-input--search"
        placeholder="Buscar por nombre o email..."
      />
      <label class="toggle-label">
        <input v-model="showInactive" type="checkbox" />
        Mostrar inactivos
      </label>
    </div>

    <!-- Error state -->
    <div v-if="loadError" class="error-banner">
      {{ loadError }}
      <button class="banner-close" @click="loadError = null">&#10005;</button>
    </div>

    <!-- Student table -->
    <div class="students-page__card">
      <AdminStudentList
        :students="students"
        :is-loading="isLoading"
      />

      <!-- Pagination -->
      <div v-if="total > pageSize" class="pagination">
        <button
          class="btn btn--secondary"
          :disabled="page === 1"
          @click="goToPage(page - 1)"
        >
          Anterior
        </button>
        <span class="pagination__info">
          Página {{ page }} de {{ totalPages }}
        </span>
        <button
          class="btn btn--secondary"
          :disabled="page >= totalPages"
          @click="goToPage(page + 1)"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { StudentItem } from '~/components/admin/StudentList.vue'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const auth = useAuthStore()
const runtimeConfig = useRuntimeConfig()
const apiBase = runtimeConfig.public.apiBase
const route = useRoute()
const router = useRouter()

const students = ref<StudentItem[]>([])
const isLoading = ref(false)
const loadError = ref<string | null>(null)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const showInactive = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

const searchInput = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function getHeaders(): Record<string, string> {
  return auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}
}

async function loadStudents() {
  isLoading.value = true
  loadError.value = null

  const params = new URLSearchParams()
  params.set('page', String(page.value))
  params.set('page_size', String(pageSize.value))
  if (searchQuery.value) params.set('q', searchQuery.value)
  // When showInactive is true, load inactive; otherwise default (active)
  if (showInactive.value) params.set('activo', 'false')

  try {
    const data = await $fetch<{ items: StudentItem[]; total: number }>(
      `${apiBase}/api/admin/students?${params.toString()}`,
      { headers: getHeaders() }
    )
    students.value = data.items
    total.value = data.total
  } catch (error: unknown) {
    let msg = 'Error al cargar los estudiantes'
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

// Debounce the search input
watch(searchInput, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    searchQuery.value = val
    page.value = 1
    loadStudents()
  }, 300)
})

watch(showInactive, () => {
  page.value = 1
  loadStudents()
})

function goToPage(newPage: number) {
  page.value = newPage
  loadStudents()
}

function clearCreatedParam() {
  router.replace({ query: {} })
}

onMounted(() => {
  loadStudents()
})

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped>
.students-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.students-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.students-page__filters {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.15s;
}

.form-input--search {
  width: 18rem;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.15);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.9375rem;
  color: #374151;
  cursor: pointer;
}

.students-page__card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.success-banner,
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.9rem;
}

.success-banner {
  background: #f0fdf4;
  border: 1px solid #86efac;
  color: #166534;
}

.error-banner {
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

.btn--primary {
  background: #1a56db;
  color: white;
}

.btn--primary:hover {
  background: #1e40af;
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
