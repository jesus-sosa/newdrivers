import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TimerBar from '../../../components/exam/TimerBar.vue'

describe('TimerBar', () => {
  it('renders the timer display with seconds-only format when remaining < 60', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 45, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').text()).toBe('45s')
  })

  it('formats time as M:SS when remaining >= 60 seconds (90s → "1:30")', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 90, total: 600 },
    })
    expect(wrapper.find('.timer-bar__time').text()).toBe('1:30')
  })

  it('pads seconds with leading zero in M:SS format (65s → "1:05")', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 65, total: 600 },
    })
    expect(wrapper.find('.timer-bar__time').text()).toBe('1:05')
  })

  it('applies timer--ok class when remaining > 50% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 70, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--ok')
    expect(wrapper.find('.timer-bar__fill').classes()).toContain('timer--ok')
  })

  it('applies timer--warning class when remaining ≤ 50% and > 20% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 40, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--warning')
    expect(wrapper.find('.timer-bar__fill').classes()).toContain('timer--warning')
  })

  it('applies timer--danger class when remaining ≤ 20% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 15, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--danger')
    expect(wrapper.find('.timer-bar__fill').classes()).toContain('timer--danger')
  })

  it('applies timer--danger class when remaining is exactly 20% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 20, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--danger')
  })

  it('applies timer--ok class when remaining is exactly 51% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 51, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--ok')
  })

  it('applies timer--warning class when remaining is exactly 50% of total', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 50, total: 100 },
    })
    expect(wrapper.find('.timer-bar__time').classes()).toContain('timer--warning')
  })

  it('sets fill bar width as a percentage style', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 30, total: 100 },
    })
    const fill = wrapper.find('.timer-bar__fill')
    expect(fill.attributes('style')).toContain('width: 30%')
  })

  it('clamps fill bar width to 0% when remaining is 0', () => {
    const wrapper = mount(TimerBar, {
      props: { remaining: 0, total: 100 },
    })
    const fill = wrapper.find('.timer-bar__fill')
    expect(fill.attributes('style')).toContain('width: 0%')
  })
})
