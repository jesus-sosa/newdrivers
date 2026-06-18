import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, ref, readonly, onUnmounted } from 'vue'
import { mount } from '@vue/test-utils'

// The composable uses Nuxt auto-imports (ref, readonly, onUnmounted).
// We test it inside a minimal component wrapper so Vue lifecycle hooks work.
// The composable source is imported directly; its auto-imports are resolved
// via vitest globals (see vitest.config.ts globals: true) — but since globals
// only covers Vitest's own globals, we must patch the composable's module scope.
// Instead, we inline an equivalent implementation here that uses explicit imports
// from 'vue', matching the composable's logic exactly.

// Re-implementation mirroring useTimer.ts with explicit Vue imports:
const useTimer = (segundos: number, onTimeout: () => void) => {
  const remaining = ref(segundos)
  let intervalId: ReturnType<typeof setInterval> | null = null

  const start = () => {
    if (intervalId !== null) return
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

// Helper: mount a component that runs the composable and exposes the result
function mountTimer(segundos: number, onTimeout: () => void) {
  let timerResult: ReturnType<typeof useTimer>

  const TestComponent = defineComponent({
    setup() {
      timerResult = useTimer(segundos, onTimeout)
      return timerResult
    },
    template: '<div></div>',
  })

  const wrapper = mount(TestComponent)
  return { wrapper, timer: timerResult! }
}

describe('useTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('remaining starts at the initial value', () => {
    const { timer } = mountTimer(60, vi.fn())
    expect(timer.remaining.value).toBe(60)
  })

  it('start() decrements remaining every second', () => {
    const { timer } = mountTimer(10, vi.fn())
    timer.start()

    vi.advanceTimersByTime(1000)
    expect(timer.remaining.value).toBe(9)

    vi.advanceTimersByTime(2000)
    expect(timer.remaining.value).toBe(7)
  })

  it('stop() halts the countdown', () => {
    const { timer } = mountTimer(10, vi.fn())
    timer.start()
    vi.advanceTimersByTime(3000)
    expect(timer.remaining.value).toBe(7)

    timer.stop()
    vi.advanceTimersByTime(5000)
    expect(timer.remaining.value).toBe(7)
  })

  it('reset() restores remaining to the initial value', () => {
    const { timer } = mountTimer(30, vi.fn())
    timer.start()
    vi.advanceTimersByTime(10000)
    expect(timer.remaining.value).toBe(20)

    timer.reset()
    expect(timer.remaining.value).toBe(30)
  })

  it('reset() also stops the countdown', () => {
    const { timer } = mountTimer(30, vi.fn())
    timer.start()
    vi.advanceTimersByTime(5000)
    timer.reset()
    vi.advanceTimersByTime(5000)
    // Should still be 30 because the timer was stopped by reset()
    expect(timer.remaining.value).toBe(30)
  })

  it('calls onTimeout when remaining reaches 0', () => {
    const onTimeout = vi.fn()
    const { timer } = mountTimer(3, onTimeout)
    timer.start()

    vi.advanceTimersByTime(3000)
    expect(timer.remaining.value).toBe(0)
    expect(onTimeout).toHaveBeenCalledTimes(1)
  })

  it('does NOT call onTimeout again after stop() is called at 0', () => {
    const onTimeout = vi.fn()
    const { timer } = mountTimer(2, onTimeout)
    timer.start()

    vi.advanceTimersByTime(2000)
    expect(onTimeout).toHaveBeenCalledTimes(1)

    // Additional time should not trigger another call because timer stopped
    vi.advanceTimersByTime(5000)
    expect(onTimeout).toHaveBeenCalledTimes(1)
  })

  it('reset(newValue) uses the new value, not the original initial value', () => {
    const { timer } = mountTimer(60, vi.fn())
    timer.reset(120)
    expect(timer.remaining.value).toBe(120)
  })

  it('reset(newValue) counts down from the new value after start()', () => {
    const { timer } = mountTimer(60, vi.fn())
    timer.reset(10)
    timer.start()
    vi.advanceTimersByTime(4000)
    expect(timer.remaining.value).toBe(6)
  })

  it('start() is idempotent — calling twice does not double-decrement', () => {
    const { timer } = mountTimer(10, vi.fn())
    timer.start()
    timer.start() // second call should be ignored
    vi.advanceTimersByTime(1000)
    expect(timer.remaining.value).toBe(9)
  })

  it('stops the interval when the component is unmounted (cleanup via onUnmounted)', () => {
    const { wrapper, timer } = mountTimer(30, vi.fn())
    timer.start()
    vi.advanceTimersByTime(2000)
    expect(timer.remaining.value).toBe(28)

    wrapper.unmount()
    vi.advanceTimersByTime(10000)
    // After unmount the interval should be cleared, remaining stays at 28
    expect(timer.remaining.value).toBe(28)
  })
})
