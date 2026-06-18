import { defineStore } from 'pinia'

interface PreguntaActual {
  orden: number
  id: number
  tema: string
  pregunta: string
  imagen_archivo: string | null
  descripcion_imagen: string | null
  opciones: Record<string, string>
}

interface ExamResumen {
  attempt_id: string
  puntuacion: number
  total_preguntas: number
  porcentaje_obtenido: number
  porcentaje_aprobacion: number
  resultado: 'aprobado' | 'reprobado'
}

interface ExamState {
  attemptId: string | null
  totalPreguntas: number
  segundosPorPregunta: number
  preguntaActual: PreguntaActual | null
  resumen: ExamResumen | null
  isLoading: boolean
  error: string | null
}

export const useExamStore = defineStore('exam', {
  state: (): ExamState => ({
    attemptId: null,
    totalPreguntas: 0,
    segundosPorPregunta: 60,
    preguntaActual: null,
    resumen: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isExamStarted: (state): boolean => !!state.attemptId,
    isExamFinished: (state): boolean => !!state.resumen,
    currentOrden: (state): number => state.preguntaActual?.orden ?? 0,
  },

  actions: {
    setExam(data: {
      attempt_id: string
      total_preguntas: number
      segundos_por_pregunta: number
      pregunta_actual: PreguntaActual
    }) {
      this.attemptId = data.attempt_id
      this.totalPreguntas = data.total_preguntas
      this.segundosPorPregunta = data.segundos_por_pregunta
      this.preguntaActual = data.pregunta_actual
      this.resumen = null
      this.error = null
    },

    nextQuestion(pregunta: PreguntaActual) {
      this.preguntaActual = pregunta
    },

    setResumen(resumen: ExamResumen) {
      this.resumen = resumen
      this.preguntaActual = null
    },

    clearExam() {
      this.attemptId = null
      this.totalPreguntas = 0
      this.segundosPorPregunta = 60
      this.preguntaActual = null
      this.resumen = null
      this.isLoading = false
      this.error = null
    },
  },
})
