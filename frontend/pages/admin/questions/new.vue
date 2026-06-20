<template>
  <div class="new-question-page">
    <div class="page-header">
      <NuxtLink to="/admin/questions" class="back-link">&larr; Volver al listado</NuxtLink>
      <h1 class="page-heading">Nueva pregunta</h1>
    </div>

    <div class="form-card">
      <p v-if="submitError" class="submit-error">{{ submitError }}</p>

      <QuestionForm
        :is-loading="isLoading"
        @submit="handleSubmit"
        @cancel="navigateTo('/admin/questions')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuestionFormData } from '~/components/admin/QuestionForm.vue'

definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const isLoading = ref(false)
const submitError = ref<string | null>(null)

async function handleSubmit(data: QuestionFormData) {
  isLoading.value = true
  submitError.value = null

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (auth.accessToken) {
      headers['Authorization'] = `Bearer ${auth.accessToken}`
    }

    await $fetch(`${apiBase}/api/questions`, {
      method: 'POST',
      body: data,
      headers,
    })

    await navigateTo('/admin/questions')
  } catch (error: unknown) {
    let msg = 'Error al crear la pregunta'
    if (error && typeof error === 'object') {
      const err = error as Record<string, unknown>
      const d = err.data as Record<string, unknown> | undefined
      if (typeof d?.detail === 'string') msg = d.detail
      else if (typeof err.message === 'string') msg = err.message
    }
    submitError.value = msg
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.new-question-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 800px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.back-link {
  font-size: 0.875rem;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.15s;
}

.back-link:hover {
  color: #1a56db;
}

.page-heading {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.submit-error {
  font-size: 0.875rem;
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 0.375rem;
  padding: 0.625rem 0.875rem;
  margin: 0;
}
</style>
