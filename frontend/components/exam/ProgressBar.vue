<template>
  <div class="progress-bar">
    <div class="progress-bar__info">
      <span>Pregunta <strong>{{ current }}</strong> de <strong>{{ total }}</strong></span>
    </div>
    <div class="progress-bar__track">
      <div
        class="progress-bar__fill"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  current: number
  total: number
}>()

const percentage = computed(() =>
  props.total > 0 ? Math.round((props.current / props.total) * 100) : 0
)
</script>

<style scoped>
.progress-bar {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.progress-bar__info {
  font-size: 0.875rem;
  color: #6b7280;
}

.progress-bar__track {
  height: 6px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: #1a56db;
  border-radius: 9999px;
  transition: width 0.4s ease;
}
</style>
