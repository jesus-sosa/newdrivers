// Provide Vue Composition API globals that Nuxt auto-imports in components.
// Without this, SFCs using computed/ref/etc. without importing from 'vue'
// would throw ReferenceError in the vitest environment.
import * as vue from 'vue'

Object.entries(vue).forEach(([key, value]) => {
  if (!(key in globalThis)) {
    ;(globalThis as Record<string, unknown>)[key] = value
  }
})
