<template>
  <div class="error-page">
    <div class="error-page__card">
      <div class="error-page__code">{{ error.statusCode }}</div>
      <h1 class="error-page__title">{{ title }}</h1>
      <p class="error-page__message">{{ message }}</p>
      <NuxtLink to="/" class="btn btn--primary">Volver al inicio</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
interface NuxtError {
  statusCode: number
  message: string
}
const props = defineProps<{ error: NuxtError }>()

const title = computed(() => {
  if (props.error.statusCode === 404) return 'Página no encontrada'
  return 'Error del servidor'
})

const message = computed(() => {
  if (props.error.statusCode === 404) return 'La página que buscas no existe o fue movida.'
  return 'Ocurrió un error inesperado. Intenta de nuevo más tarde.'
})
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  padding: 2rem;
}

.error-page__card {
  text-align: center;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.error-page__code {
  font-size: 5rem;
  font-weight: 800;
  color: #d1d5db;
  line-height: 1;
}

.error-page__title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.error-page__message {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.9375rem;
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
  background: #1e40af;
}
</style>
