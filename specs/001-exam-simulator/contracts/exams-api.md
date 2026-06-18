# Contrato API: Sesión de Examen

**Base URL**: `/api/exams`
**Autenticación**: JWT requerido en todos los endpoints.

---

## POST /api/exams/start

Inicia un nuevo intento de examen para el estudiante autenticado.

**Roles permitidos**: `estudiante`

**Request Body**: Sin body.

**Validaciones previas (el servidor verifica)**:
- `configuracion_examen.porcentaje_aprobacion IS NOT NULL`
- Total de preguntas activas ≥ `configuracion_examen.num_preguntas`

**Comportamiento**:
1. Lee la configuración actual (snapshot: `num_preguntas`, `porcentaje_aprobacion`)
2. Selecciona N preguntas activas aleatoriamente (Fisher-Yates en aplicación)
3. Crea `intentos_examen` con `finalizado_at=NULL`
4. Crea N filas en `respuestas_intento` con `opcion_seleccionada=NULL`
5. Retorna `attempt_id` + primera pregunta (orden=1) + configuración del timer

**Response 201 Created**:
```json
{
  "attempt_id": "uuid",
  "total_preguntas": 20,
  "segundos_por_pregunta": 60,
  "pregunta_actual": {
    "orden": 1,
    "id": 13,
    "tema": "Formas de señales de tránsito",
    "pregunta": "¿Qué forma geométrica identifica la señal de ALTO?",
    "imagen_archivo": "imagenes_senales/pg11_img04_109x103.jpeg",
    "descripcion_imagen": "Señal de ALTO octagonal roja",
    "opciones": {
      "A": "Círculo",
      "B": "Triángulo",
      "C": "Octágono",
      "D": "Rombo"
    }
  }
}
```

> **Nota**: `fundamento_juridico` y `respuesta_correcta` NO se incluyen en la respuesta
> durante el examen para evitar que el cliente los exponga.

**Errores**:
- `409` — sistema no configurado (`porcentaje_aprobacion` no establecido)
- `409` — banco de preguntas insuficiente

---

## GET /api/exams/{attempt_id}

Recupera el estado actual del examen (útil para reconexión).

**Roles permitidos**: `estudiante` (solo su propio intento)

**Response 200 OK**:
```json
{
  "attempt_id": "uuid",
  "total_preguntas": 20,
  "segundos_por_pregunta": 60,
  "respondidas": 7,
  "estado": "en_curso",
  "pregunta_actual": {
    "orden": 8,
    "id": 25,
    "tema": "Semáforo",
    "pregunta": "¿Qué debe hacer el conductor cuando el semáforo muestra luz roja?",
    "imagen_archivo": null,
    "descripcion_imagen": null,
    "opciones": {
      "A": "Reducir velocidad y continuar",
      "B": "Detenerse completamente",
      "C": "Continuar con precaución",
      "D": "Solo detenerse en avenidas principales"
    }
  }
}
```

Si el examen ya está finalizado, `estado = "finalizado"` y `pregunta_actual = null`.

**Errores**:
- `404` — intento no encontrado o no pertenece al estudiante

---

## POST /api/exams/{attempt_id}/answer

Registra la respuesta del estudiante para la pregunta actual.

**Roles permitidos**: `estudiante` (solo su propio intento)

**Request Body**:
```json
{
  "orden": 8,
  "opcion_seleccionada": "B",
  "tiempo_agotado": false
}
```

Cuando el timer expira sin respuesta:
```json
{
  "orden": 8,
  "opcion_seleccionada": null,
  "tiempo_agotado": true
}
```

**Comportamiento**:
1. Valida que `orden` corresponde a la siguiente pregunta pendiente del intento
2. Actualiza `respuestas_intento`: establece `opcion_seleccionada`, `es_correcta`, `tiempo_agotado`, `respondida_at`
3. Determina si hay más preguntas pendientes
4. Si quedan preguntas: retorna la siguiente
5. Si era la última: finaliza el examen automáticamente y retorna resumen

**Response 200 OK — hay más preguntas**:
```json
{
  "orden_respondido": 8,
  "siguiente_pregunta": {
    "orden": 9,
    "id": 41,
    "tema": "Señales preventivas",
    "pregunta": "¿Qué indica la señal preventiva 'Alto próximo'?",
    "imagen_archivo": "imagenes_senales/pg15_img03_101x96.jpeg",
    "descripcion_imagen": "Señal preventiva amarilla de alto próximo",
    "opciones": {
      "A": "Semáforo a 500 metros",
      "B": "Cercanía de una señal de ALTO",
      "C": "Zona de reducción de velocidad",
      "D": "Proximidad de un cruce peatonal"
    }
  }
}
```

**Response 200 OK — última pregunta (examen finalizado)**:
```json
{
  "orden_respondido": 20,
  "siguiente_pregunta": null,
  "examen_finalizado": true,
  "resumen": {
    "attempt_id": "uuid",
    "puntuacion": 15,
    "total_preguntas": 20,
    "porcentaje_obtenido": 75.0,
    "porcentaje_aprobacion": 70.0,
    "resultado": "aprobado"
  }
}
```

**Errores**:
- `400` — `orden` no coincide con la siguiente pregunta pendiente
- `400` — `opcion_seleccionada` no es A/B/C/D (y no es null)
- `409` — el intento ya está finalizado

---

## POST /api/exams/{attempt_id}/finish

Finaliza manualmente el examen (por ejemplo, si el estudiante quiere terminar antes).

**Roles permitidos**: `estudiante` (solo su propio intento)

**Request Body**: Sin body.

**Comportamiento**: Las preguntas no respondidas se marcan con `tiempo_agotado=false`, `es_correcta=false`.

**Response 200 OK**: Mismo formato que el resumen en `/answer` cuando es la última pregunta.

**Errores**:
- `409` — el intento ya está finalizado

---

## GET /api/exams/{attempt_id}/results

Devuelve los resultados completos de un intento finalizado, con retroalimentación por pregunta.

**Roles permitidos**: `estudiante` (su propio intento), `admin` (cualquier intento)

**Response 200 OK**:
```json
{
  "attempt_id": "uuid",
  "iniciado_at": "2026-06-17T10:00:00Z",
  "finalizado_at": "2026-06-17T10:18:32Z",
  "puntuacion": 15,
  "total_preguntas": 20,
  "porcentaje_obtenido": 75.0,
  "porcentaje_aprobacion": 70.0,
  "resultado": "aprobado",
  "preguntas": [
    {
      "orden": 1,
      "id": 13,
      "tema": "Formas de señales de tránsito",
      "pregunta": "¿Qué forma geométrica identifica la señal de ALTO?",
      "imagen_archivo": "imagenes_senales/pg11_img04_109x103.jpeg",
      "opciones": {
        "A": "Círculo",
        "B": "Triángulo",
        "C": "Octágono",
        "D": "Rombo"
      },
      "opcion_seleccionada": "A",
      "respuesta_correcta": "C",
      "es_correcta": false,
      "tiempo_agotado": false,
      "fundamento_juridico": "Manual de Señalamiento SCT: La forma de Octágono corresponde únicamente a la señal de Detención total (ALTO)."
    }
  ]
}
```

**Errores**:
- `404` — intento no encontrado
- `409` — el intento aún no ha finalizado

---

## GET /api/exams/history

Devuelve el historial de intentos del estudiante autenticado.

**Roles permitidos**: `estudiante`

**Query Parameters**:
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | integer | `1` | Página |
| `page_size` | integer | `10` | Resultados por página |

**Response 200 OK**:
```json
{
  "total": 5,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "attempt_id": "uuid",
      "iniciado_at": "2026-06-17T10:00:00Z",
      "finalizado_at": "2026-06-17T10:18:32Z",
      "puntuacion": 15,
      "total_preguntas": 20,
      "resultado": "aprobado"
    }
  ]
}
```
