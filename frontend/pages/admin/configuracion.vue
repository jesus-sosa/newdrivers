<template>
  <div class="coming-soon">
    <div class="coming-soon__icon">⚙️</div>
    <h2>Configuración del Examen</h2>
    <p>Esta sección estará disponible en la próxima iteración (US4).</p>
    <p class="coming-soon__tip">
      Por ahora puedes ajustar la configuración directamente en la base de datos
      o usando el endpoint <code>PUT /api/admin/config</code> cuando esté disponible.
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})
</script>

<style scoped>
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #6b7280;
}

.coming-soon__icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem;
}

p {
  margin: 0.25rem 0;
  font-size: 0.9375rem;
}

.coming-soon__tip {
  margin-top: 1rem;
  font-size: 0.875rem;
  background: #f3f4f6;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  max-width: 480px;
}

code {
  font-family: monospace;
  background: #e5e7eb;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
}
</style>
