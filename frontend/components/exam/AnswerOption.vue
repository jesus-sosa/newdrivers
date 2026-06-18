<template>
  <button
    class="answer-option"
    :class="{
      'answer-option--selected': selected,
      'answer-option--disabled': disabled,
    }"
    :disabled="disabled"
    @click="$emit('select', letter)"
  >
    <span class="answer-option__letter">{{ letter }}</span>
    <span class="answer-option__text">{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  letter: string
  text: string
  selected?: boolean
  disabled?: boolean
}>()

defineEmits<{
  select: [letter: string]
}>()
</script>

<style scoped>
.answer-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.875rem 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
  font-size: 0.9375rem;
}

.answer-option:hover:not(:disabled) {
  border-color: #1a56db;
  background: #eff6ff;
}

.answer-option--selected {
  border-color: #1a56db;
  background: #eff6ff;
}

.answer-option--disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.answer-option--selected.answer-option--disabled {
  opacity: 1;
}

.answer-option__letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f3f4f6;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
  color: #374151;
  flex-shrink: 0;
}

.answer-option--selected .answer-option__letter {
  background: #1a56db;
  color: white;
}

.answer-option__text {
  flex: 1;
  color: #374151;
  line-height: 1.4;
}
</style>
