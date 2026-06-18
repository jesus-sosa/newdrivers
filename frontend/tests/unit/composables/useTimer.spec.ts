import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { useTimer } from '~/composables/useTimer'

// Helper: mount a component that runs the composable so Vue lifecycle hooks work
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
    timer.start()
    vi.advanceTimersByTime(1000)
    expect(timer.remaining.value).toBe(9)
  })

  it('stops the interval when the component is unmounted', () => {
    const { wrapper, timer } = mountTimer(30, vi.fn())
    timer.start()
    vi.advanceTimersByTime(2000)
    expect(timer.remaining.value).toBe(28)

    wrapper.unmount()
    vi.advanceTimersByTime(10000)
    expect(timer.remaining.value).toBe(28)
  })
})
