import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, nextTick } from 'vue'

// ---------------------------------------------------------------------------
// Nuxt-specific globals not provided by setup.ts
// ---------------------------------------------------------------------------
const navigateTo = vi.fn()
globalThis.navigateTo = navigateTo

const definePageMeta = vi.fn()
globalThis.definePageMeta = definePageMeta

// Stub NuxtLink as a simple anchor element
const NuxtLink = defineComponent({
  name: 'NuxtLink',
  props: { to: String },
  template: '<a :href="to"><slot /></a>',
})
globalThis.NuxtLink = NuxtLink

// useRuntimeConfig fallback (consumed by the real useAuth, but we mock useAuth)
globalThis.useRuntimeConfig = vi.fn(() => ({ public: { apiBase: '' } }))

// ---------------------------------------------------------------------------
// Mock useAuth so we control the login spy
// ---------------------------------------------------------------------------
const mockLogin = vi.fn()

vi.mock('~/composables/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    isLoading: ref(false),
  }),
}))

// Make useAuth available as a global (Nuxt auto-import style)
globalThis.useAuth = () => ({ login: mockLogin, isLoading: ref(false) })

// ---------------------------------------------------------------------------
// Mock useAuthStore so onMounted does not throw
// ---------------------------------------------------------------------------
vi.mock('~/stores/auth', () => ({
  useAuthStore: () => ({
    hydrateFromStorage: vi.fn().mockResolvedValue(undefined),
    isAuthenticated: false,
    isAdmin: false,
    isEditor: false,
  }),
}))

// Make useAuthStore available as a global (Nuxt auto-import style)
globalThis.useAuthStore = () => ({
  hydrateFromStorage: vi.fn().mockResolvedValue(undefined),
  isAuthenticated: false,
  isAdmin: false,
  isEditor: false,
})

// ---------------------------------------------------------------------------
// Import the page AFTER mocks are registered
// ---------------------------------------------------------------------------
import LoginPage from '../../pages/login.vue'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function mountLogin() {
  return mount(LoginPage, {
    global: {
      components: { NuxtLink },
    },
  })
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe('Login page – form validation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mockLogin.mockReset()
    navigateTo.mockReset()
    mockLogin.mockResolvedValue({ success: true })
  })

  // -------------------------------------------------------------------------
  // R1: Error visible if email is empty — no API call
  // -------------------------------------------------------------------------

  it('shows email-required error and does NOT call login when email is empty', async () => {
    const wrapper = mountLogin()

    // Set a valid password but leave email empty
    await wrapper.find('#password').setValue('validpassword123')
    await wrapper.find('form').trigger('submit')
    await nextTick()

    expect(mockLogin).not.toHaveBeenCalled()
    const errorEl = wrapper.find('.form-error')
    expect(errorEl.exists()).toBe(true)
    expect(errorEl.text()).toContain('correo')
  })

  // -------------------------------------------------------------------------
  // R2: Error visible if password < 8 chars — no API call
  // -------------------------------------------------------------------------

  it('shows password-length error and does NOT call login when password is shorter than 8 chars', async () => {
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('user@example.com')
    await wrapper.find('#password').setValue('abc')
    await wrapper.find('form').trigger('submit')
    await nextTick()

    expect(mockLogin).not.toHaveBeenCalled()
    const errorEl = wrapper.find('.form-error')
    expect(errorEl.exists()).toBe(true)
    expect(errorEl.text()).toContain('8 caracteres')
  })

  // -------------------------------------------------------------------------
  // R3: No API call with invalid data (edge: password exactly 7 chars)
  // -------------------------------------------------------------------------

  it('does NOT call login when password is exactly 7 characters (below minimum)', async () => {
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('user@example.com')
    await wrapper.find('#password').setValue('1234567')
    await wrapper.find('form').trigger('submit')
    await nextTick()

    expect(mockLogin).not.toHaveBeenCalled()
  })

  // -------------------------------------------------------------------------
  // Server error display
  // -------------------------------------------------------------------------

  it('displays server error returned by the login composable', async () => {
    mockLogin.mockResolvedValue({ success: false, error: 'Credenciales inválidas' })
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('user@example.com')
    await wrapper.find('#password').setValue('validpassword123')
    await wrapper.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    const errorEl = wrapper.find('.form-error')
    expect(errorEl.exists()).toBe(true)
    expect(errorEl.text()).toContain('Credenciales inválidas')
  })

  it('shows fallback error text when composable returns no error message', async () => {
    mockLogin.mockResolvedValue({ success: false })
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('user@example.com')
    await wrapper.find('#password').setValue('validpassword123')
    await wrapper.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    const errorEl = wrapper.find('.form-error')
    expect(errorEl.exists()).toBe(true)
    expect(errorEl.text()).toContain('Error al iniciar sesión')
  })

  // -------------------------------------------------------------------------
  // Successful login
  // -------------------------------------------------------------------------

  it('calls login with correct credentials and navigates away on successful login', async () => {
    mockLogin.mockResolvedValue({ success: true })
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('admin@example.com')
    await wrapper.find('#password').setValue('supersecret')
    await wrapper.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(mockLogin).toHaveBeenCalledWith('admin@example.com', 'supersecret')
    expect(navigateTo).toHaveBeenCalled()
  })

  it('does NOT navigate after a failed login', async () => {
    mockLogin.mockResolvedValue({ success: false, error: 'Bad credentials' })
    const wrapper = mountLogin()

    await wrapper.find('#email').setValue('user@example.com')
    await wrapper.find('#password').setValue('wrongpassword')
    await wrapper.find('form').trigger('submit')
    await nextTick()
    await nextTick()

    expect(navigateTo).not.toHaveBeenCalled()
  })

  // -------------------------------------------------------------------------
  // No error before submission
  // -------------------------------------------------------------------------

  it('error message is not visible before any submission', () => {
    const wrapper = mountLogin()
    expect(wrapper.find('.form-error').exists()).toBe(false)
  })
})
