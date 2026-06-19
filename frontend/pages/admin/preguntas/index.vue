<template>
  <div class="coming-soon">
    <div class="coming-soon__icon">📋</div>
    <h2>Banco de Preguntas</h2>
    <p>Esta sección estará disponible en la próxima iteración (US3).</p>
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
</style>
