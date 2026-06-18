<template>
  <div v-if="fundamento" class="legal-block">
    <p class="legal-block__label">Fundamento jurídico</p>
    <p class="legal-block__text">{{ fundamento }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  fundamento: string | null | undefined
}>()
</script>

<style scoped>
.legal-block {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  padding: 0.75rem 1rem;
  border-radius: 0 0.375rem 0.375rem 0;
  margin-top: 0.75rem;
}

.legal-block__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #d97706;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.25rem;
}

.legal-block__text {
  font-size: 0.875rem;
  color: #78350f;
  margin: 0;
  line-height: 1.5;
}
</style>
