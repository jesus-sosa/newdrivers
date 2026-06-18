/**
 * Timer regresivo para preguntas de examen.
 * Inicia desde `segundos`, llama `onTimeout` cuando llega a 0.
 */
export const useTimer = (segundos: number, onTimeout: () => void) => {
  const remaining = ref(segundos)
  let intervalId: ReturnType<typeof setInterval> | null = null

  const start = () => {
    if (intervalId !== null) return  // ya corriendo
    intervalId = setInterval(() => {
      remaining.value--
      if (remaining.value <= 0) {
        stop()
        onTimeout()
      }
    }, 1000)
  }

  const stop = () => {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  const reset = (newSegundos?: number) => {
    stop()
    remaining.value = newSegundos ?? segundos
  }

  onUnmounted(() => {
    stop()
  })

  return {
    remaining: readonly(remaining),
    start,
    stop,
    reset,
  }
}
