<template>
  <div class="student-list">
    <!-- Loading state -->
    <div v-if="isLoading" class="student-list__loading">
      Cargando estudiantes...
    </div>

    <!-- Empty state -->
    <div v-else-if="students.length === 0" class="student-list__empty">
      No se encontraron estudiantes.
    </div>

    <!-- Table -->
    <div v-else class="student-list__table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Estado</th>
            <th>Total intentos</th>
            <th>Último resultado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td>{{ student.nombre_completo }}</td>
            <td>{{ student.email }}</td>
            <td>
              <span
                class="badge"
                :class="student.activo ? 'badge--green' : 'badge--red'"
              >
                {{ student.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td>{{ student.total_intentos }}</td>
            <td>
              <span
                v-if="student.ultimo_resultado"
                class="badge"
                :class="student.ultimo_resultado === 'aprobado' ? 'badge--green' : 'badge--red'"
              >
                {{ student.ultimo_resultado === 'aprobado' ? 'Aprobado' : 'Reprobado' }}
              </span>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <NuxtLink
                v-if="auth.isAdmin"
                :to="`/admin/students/${student.id}`"
                class="action-link"
              >
                Ver detalle
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

export interface StudentItem {
  id: string
  nombre_completo: string
  email: string
  activo: boolean
  total_intentos: number
  ultimo_resultado: string | null
  created_at: string
}

interface Props {
  students: StudentItem[]
  isLoading: boolean
}

defineProps<Props>()

const auth = useAuthStore()
</script>

<style scoped>
.student-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.student-list__search {
  max-width: 20rem;
}

.student-list__loading,
.student-list__empty {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.student-list__table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.data-table th,
.data-table td {
  padding: 0.625rem 0.875rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
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

.action-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.action-link:hover {
  text-decoration: underline;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
  outline: none;
  transition: border-color 0.15s;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.15);
}
</style>
