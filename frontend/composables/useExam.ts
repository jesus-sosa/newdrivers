export const useExam = () => {
  const exam = useExamStore()
  const auth = useAuthStore()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const authHeaders = computed(() => ({
    Authorization: `Bearer ${auth.accessToken}`,
  }))

  const startExam = async (): Promise<{ success: boolean; error?: string }> => {
    exam.isLoading = true
    exam.error = null
    try {
      const data = await $fetch<{
        attempt_id: string
        total_preguntas: number
        segundos_por_pregunta: number
        pregunta_actual: {
          orden: number
          id: number
          tema: string
          pregunta: string
          imagen_archivo: string | null
          descripcion_imagen: string | null
          opciones: Record<string, string>
        }
      }>(`${apiBase}/api/exams/start`, {
        method: 'POST',
        headers: authHeaders.value,
      })
      exam.setExam(data)
      return { success: true }
    } catch (error: unknown) {
      let msg = 'Error al iniciar el examen'
      if (error && typeof error === 'object') {
        const err = error as Record<string, unknown>
        const data = err.data as Record<string, unknown> | undefined
        if (typeof data?.detail === 'string') msg = data.detail
      }
      exam.error = msg
      return { success: false, error: msg }
    } finally {
      exam.isLoading = false
    }
  }

  const submitAnswer = async (
    orden: number,
    opcionSeleccionada: string | null,
    tiempoAgotado: boolean = false,
  ): Promise<{ finished: boolean; error?: string }> => {
    if (!exam.attemptId) return { finished: false, error: 'No hay examen activo' }

    exam.isLoading = true
    try {
      const data = await $fetch<{
        orden_respondido: number
        siguiente_pregunta: {
          orden: number
          id: number
          tema: string
          pregunta: string
          imagen_archivo: string | null
          descripcion_imagen: string | null
          opciones: Record<string, string>
        } | null
        examen_finalizado?: boolean
        resumen?: {
          attempt_id: string
          puntuacion: number
          total_preguntas: number
          porcentaje_obtenido: number
          porcentaje_aprobacion: number
          resultado: 'aprobado' | 'reprobado'
        }
      }>(`${apiBase}/api/exams/${exam.attemptId}/answer`, {
        method: 'POST',
        headers: authHeaders.value,
        body: {
          orden,
          opcion_seleccionada: opcionSeleccionada,
          tiempo_agotado: tiempoAgotado,
        },
      })

      if (data.examen_finalizado) {
        if (data.resumen) {
          exam.setResumen(data.resumen)
        } else {
          exam.error = 'El examen finalizó pero no se recibió el resumen'
        }
        return { finished: true }
      }

      if (data.siguiente_pregunta) {
        exam.nextQuestion(data.siguiente_pregunta)
      }

      return { finished: false }
    } catch (error: unknown) {
      let msg = 'Error al registrar respuesta'
      if (error && typeof error === 'object') {
        const err = error as Record<string, unknown>
        const data = err.data as Record<string, unknown> | undefined
        if (typeof data?.detail === 'string') msg = data.detail
      }
      return { finished: false, error: msg }
    } finally {
      exam.isLoading = false
    }
  }

  const finishEarly = async (): Promise<{ success: boolean }> => {
    if (!exam.attemptId) return { success: false }
    try {
      const data = await $fetch<{
        attempt_id: string
        puntuacion: number
        total_preguntas: number
        porcentaje_obtenido: number
        porcentaje_aprobacion: number
        resultado: 'aprobado' | 'reprobado'
      }>(`${apiBase}/api/exams/${exam.attemptId}/finish`, {
        method: 'POST',
        headers: authHeaders.value,
      })
      exam.setResumen(data)
      return { success: true }
    } catch {
      exam.error = 'Error al finalizar el examen'
      return { success: false }
    }
  }

  const fetchResults = async (attemptId: string) => {
    try {
      return await $fetch<{
        attempt_id: string
        iniciado_at: string
        finalizado_at: string
        puntuacion: number
        total_preguntas: number
        porcentaje_obtenido: number
        porcentaje_aprobacion: number
        resultado: 'aprobado' | 'reprobado'
        preguntas: Array<{
          orden: number
          tema: string
          pregunta: string
          opciones: Record<string, string>
          opcion_seleccionada: string | null
          respuesta_correcta: string
          es_correcta: boolean | null
          tiempo_agotado: boolean
          fundamento_juridico: string | null
        }>
      }>(`${apiBase}/api/exams/${attemptId}/results`, {
        headers: authHeaders.value,
      })
    } catch {
      return null
    }
  }

  const fetchHistory = async (page = 1, pageSize = 10) => {
    try {
      return await $fetch<{
        total: number
        page: number
        page_size: number
        items: Array<{
          attempt_id: string
          iniciado_at: string
          finalizado_at: string | null
          puntuacion: number | null
          total_preguntas: number
          resultado: string | null
        }>
      }>(`${apiBase}/api/exams/history`, {
        headers: authHeaders.value,
        query: { page, page_size: pageSize },
      })
    } catch {
      return { total: 0, page, page_size: pageSize, items: [] }
    }
  }

  return {
    startExam,
    submitAnswer,
    finishEarly,
    fetchResults,
    fetchHistory,
    isLoading: computed(() => exam.isLoading),
    isExamStarted: computed(() => exam.isExamStarted),
    isExamFinished: computed(() => exam.isExamFinished),
    attemptId: computed(() => exam.attemptId),
    preguntaActual: computed(() => exam.preguntaActual),
    resumen: computed(() => exam.resumen),
    totalPreguntas: computed(() => exam.totalPreguntas),
    segundosPorPregunta: computed(() => exam.segundosPorPregunta),
    currentOrden: computed(() => exam.currentOrden),
    error: computed(() => exam.error),
  }
}
