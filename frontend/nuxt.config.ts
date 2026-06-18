// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: ['@pinia/nuxt'],

  runtimeConfig: {
    // Variables privadas del servidor (no expuestas al cliente)
    apiBase: process.env.NUXT_API_BASE || 'http://exams-backend:8000',
    // Variables públicas (expuestas al cliente como NUXT_PUBLIC_*)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },

  nitro: {
    // Configuración del servidor Nitro para producción
  },

  typescript: {
    strict: false,
    typeCheck: false
  },

  css: [],

  app: {
    head: {
      title: 'New Drivers — Simulador de Examen',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Simulador de examen de manejo para New Drivers' }
      ]
    }
  }
})
