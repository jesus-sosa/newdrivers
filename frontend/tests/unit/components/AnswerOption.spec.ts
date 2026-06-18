import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AnswerOption from '../../../components/exam/AnswerOption.vue'

describe('AnswerOption', () => {
  it('renders the letter correctly', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'A', text: 'Turn left at the intersection' },
    })
    expect(wrapper.find('.answer-option__letter').text()).toBe('A')
  })

  it('renders the text correctly', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'B', text: 'Stop before the crosswalk' },
    })
    expect(wrapper.find('.answer-option__text').text()).toBe('Stop before the crosswalk')
  })

  it('emits "select" event with the letter when clicked', async () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'C', text: 'Yield to pedestrians' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')![0]).toEqual(['C'])
  })

  it('applies answer-option--selected class when selected prop is true', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'D', text: 'Accelerate through', selected: true },
    })
    expect(wrapper.find('button').classes()).toContain('answer-option--selected')
  })

  it('does NOT apply answer-option--selected class when selected prop is false', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'A', text: 'Some option', selected: false },
    })
    expect(wrapper.find('button').classes()).not.toContain('answer-option--selected')
  })

  it('does NOT apply answer-option--selected class when selected prop is omitted', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'A', text: 'Some option' },
    })
    expect(wrapper.find('button').classes()).not.toContain('answer-option--selected')
  })

  it('has disabled attribute on button when disabled prop is true', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'B', text: 'Disabled option', disabled: true },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('applies answer-option--disabled class when disabled prop is true', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'B', text: 'Disabled option', disabled: true },
    })
    expect(wrapper.find('button').classes()).toContain('answer-option--disabled')
  })

  it('does NOT have disabled attribute when disabled prop is false', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'A', text: 'Enabled option', disabled: false },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('does NOT emit "select" when clicked while disabled', async () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'C', text: 'Disabled option', disabled: true },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('select')).toBeFalsy()
  })

  it('renders with both selected and disabled props simultaneously', () => {
    const wrapper = mount(AnswerOption, {
      props: { letter: 'A', text: 'Selected and disabled', selected: true, disabled: true },
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('answer-option--selected')
    expect(button.classes()).toContain('answer-option--disabled')
    expect(button.attributes('disabled')).toBeDefined()
  })
})
