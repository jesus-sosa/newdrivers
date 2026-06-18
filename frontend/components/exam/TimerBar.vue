<template>
  <div class="timer-bar">
    <div class="timer-bar__track">
      <div
        class="timer-bar__fill"
        :class="timerClass"
        :style="{ width: `${percentage}%` }"
      />
    </div>
    <span class="timer-bar__time" :class="timerClass">
      {{ formattedTime }}
    </span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  remaining: number
  total: number
}>()

const percentage = computed(() => Math.max(0, Math.min(100, (props.remaining / props.total) * 100)))

const timerClass = computed(() => {
  if (percentage.value > 50) return 'timer--ok'
  if (percentage.value > 20) return 'timer--warning'
  return 'timer--danger'
})

const formattedTime = computed(() => {
  const mins = Math.floor(props.remaining / 60)
  const secs = props.remaining % 60
  return mins > 0
    ? `${mins}:${String(secs).padStart(2, '0')}`
    : `${secs}s`
})
</script>

<style scoped>
.timer-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.timer-bar__track {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.timer-bar__fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 1s linear, background-color 0.3s;
}

.timer-bar__time {
  font-size: 0.875rem;
  font-weight: 600;
  min-width: 3rem;
  text-align: right;
}

.timer--ok { background-color: #22c55e; color: #15803d; }
.timer--warning { background-color: #f59e0b; color: #d97706; }
.timer--danger { background-color: #ef4444; color: #dc2626; }
</style>
