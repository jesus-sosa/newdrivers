# Data Model: Simulador de Examen de Manejo

**Feature**: 001-exam-simulator
**Date**: 2026-06-17
**Database**: `newdrivers_exams` (instancia PostgreSQL compartida en `newdrivers-infra`)

---

## Diagrama de relaciones

```
users (1) ──────────────────────────────── (N) intentos_examen
  │                                               │
  │ (created_by)                                  │ (N)
  ▼                                               ▼
configuracion_examen (singleton)         respuestas_intento (N)
                                               │
preguntas (1) ─────────────────────────── (N) respuestas_intento
```

---

## Tabla: `users`

Representa a cualquier persona con acceso al sistema (admin, editor o estudiante).

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Identificador único |
| `nombre_completo` | `VARCHAR(255)` | NOT NULL | Nombre y apellidos |
| `email` | `VARCHAR(255)` | NOT NULL, UNIQUE | Correo electrónico (login) |
| `password_hash` | `VARCHAR(255)` | NOT NULL | Hash bcrypt de la contraseña |
| `rol` | `VARCHAR(20)` | NOT NULL, CHECK IN ('admin','editor','estudiante') | Rol RBAC |
| `activo` | `BOOLEAN` | NOT NULL, DEFAULT true | Permite deshabilitar cuentas |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Fecha de registro |
| `updated_at` | `TIMESTAMPTZ` | | Última modificación |

**Índices**: `email` (UNIQUE), `rol` (para filtros admin).

**Reglas de negocio**:
- El rol solo puede ser asignado/modificado por un `admin`.
- Los usuarios con `activo=false` no pueden autenticarse.
- No se permite eliminar usuarios con intentos de examen registrados (integridad referencial).

---

## Tabla: `preguntas`

Banco de preguntas del simulador. Estructura compatible con el DDL provisto.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `SERIAL` | PK | Identificador autoincremental |
| `tema` | `VARCHAR(60)` | NOT NULL | Categoría temática (ej. "Señales restrictivas") |
| `pregunta` | `TEXT` | NOT NULL | Enunciado de la pregunta |
| `imagen_archivo` | `VARCHAR(255)` | | Ruta relativa a la imagen de apoyo (nullable) |
| `descripcion_imagen` | `TEXT` | | Texto alternativo / descripción de la imagen |
| `opcion_a` | `TEXT` | NOT NULL | Opción A |
| `opcion_b` | `TEXT` | NOT NULL | Opción B |
| `opcion_c` | `TEXT` | NOT NULL | Opción C |
| `opcion_d` | `TEXT` | NOT NULL | Opción D |
| `respuesta_correcta` | `CHAR(1)` | NOT NULL, CHECK IN ('A','B','C','D') | Letra de la opción correcta |
| `fundamento_juridico` | `TEXT` | | Base legal o explicación de la respuesta correcta |
| `activa` | `BOOLEAN` | NOT NULL, DEFAULT true | `false` = soft-delete; pregunta no aparece en nuevos exámenes |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | `TIMESTAMPTZ` | | Última modificación |

**Índices**: `tema` (para filtros en panel admin), `activa` (para generación de exámenes).

**Reglas de negocio**:
- Una pregunta con `activa=false` no se incluye en nuevos exámenes, pero sus respuestas en
  intentos pasados se conservan (integridad referencial).
- Si una pregunta está referenciada en un intento activo (`finalizado_at IS NULL`), no puede
  cambiar su `respuesta_correcta` hasta que el intento finalice.
- La ruta en `imagen_archivo` es relativa al directorio de archivos estáticos
  (ej. `imagenes_senales/pg04_img03_184x81.jpeg`).

**Temas conocidos del banco inicial**:
- Requisitos
- Equipos instalados
- Responsabilidad vial
- Formas de señales de tránsito
- Colores de señales de tránsito
- Señales restrictivas
- Señales preventivas
- Semáforo
- Marca pavimental
- Conducción segura

---

## Tabla: `configuracion_examen`

Singleton (siempre una sola fila con `id=1`). Parámetros globales del simulador.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `INTEGER` | PK, DEFAULT 1, CHECK (id=1) | Siempre es 1 |
| `num_preguntas` | `INTEGER` | NOT NULL, DEFAULT 20, CHECK (> 0) | Preguntas por examen |
| `segundos_por_pregunta` | `INTEGER` | NOT NULL, DEFAULT 60, CHECK (> 0) | Timer por pregunta |
| `porcentaje_aprobacion` | `NUMERIC(5,2)` | CHECK (0 <= val <= 100) | NULL = no configurado aún |
| `updated_at` | `TIMESTAMPTZ` | | Última modificación |
| `updated_by` | `UUID` | FK → users(id) | Quién hizo el último cambio |

**Reglas de negocio**:
- `porcentaje_aprobacion IS NULL` bloquea el inicio de exámenes hasta que el admin lo configure.
- El sistema valida que `num_preguntas` ≤ total de preguntas activas en el banco antes de permitir
  iniciar un examen.

---

## Tabla: `intentos_examen`

Registro de cada sesión de examen de un estudiante.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Identificador único del intento |
| `estudiante_id` | `UUID` | NOT NULL, FK → users(id) | Estudiante que realizó el examen |
| `num_preguntas` | `INTEGER` | NOT NULL | Snapshot del config al momento del inicio |
| `porcentaje_aprobacion` | `NUMERIC(5,2)` | NOT NULL | Snapshot del config al momento del inicio |
| `puntuacion` | `INTEGER` | | Número de respuestas correctas (NULL hasta finalizar) |
| `resultado` | `VARCHAR(10)` | CHECK IN ('aprobado','reprobado') | NULL hasta finalizar |
| `iniciado_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Inicio del examen |
| `finalizado_at` | `TIMESTAMPTZ` | | NULL = examen en curso |

**Índices**: `estudiante_id`, `finalizado_at`, `resultado`.

**Reglas de negocio**:
- `num_preguntas` y `porcentaje_aprobacion` se copian desde `configuracion_examen` al iniciar
  el intento (snapshot) para que cambios futuros en config no afecten intentos en curso.
- Un estudiante puede tener múltiples intentos simultáneamente (raro, pero no se bloquea en v1).
- Al finalizar: `puntuacion = COUNT(respuestas_intento WHERE es_correcta=true)`;
  `resultado = 'aprobado'` si `(puntuacion / num_preguntas * 100) >= porcentaje_aprobacion`.

---

## Tabla: `respuestas_intento`

Una fila por cada pregunta presentada en un intento. Se crea al iniciar el examen.

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Identificador único |
| `intento_id` | `UUID` | NOT NULL, FK → intentos_examen(id) | Intento al que pertenece |
| `pregunta_id` | `INTEGER` | NOT NULL, FK → preguntas(id) | Pregunta presentada |
| `orden` | `INTEGER` | NOT NULL | Posición en el examen (1, 2, … N) |
| `opcion_seleccionada` | `CHAR(1)` | CHECK IN ('A','B','C','D') | Respuesta del estudiante (NULL si no respondió) |
| `es_correcta` | `BOOLEAN` | | NULL hasta responder; false si tiempo agotado |
| `tiempo_agotado` | `BOOLEAN` | NOT NULL, DEFAULT false | true si el timer expiró antes de responder |
| `respondida_at` | `TIMESTAMPTZ` | | Momento en que se registró la respuesta |

**Restricción única**: `(intento_id, pregunta_id)` — una pregunta no se repite en el mismo intento.
**Restricción única**: `(intento_id, orden)` — cada posición es única en el intento.

**Reglas de negocio**:
- Las N filas de `respuestas_intento` se crean todas al iniciar el intento (preguntas ya
  seleccionadas y ordenadas).
- `opcion_seleccionada=NULL` + `tiempo_agotado=true` → el timer expiró.
- `opcion_seleccionada=NULL` + `tiempo_agotado=false` → pregunta aún no alcanzada (examen en curso).
- `es_correcta` se calcula al recibir la respuesta:
  `es_correcta = (opcion_seleccionada == preguntas.respuesta_correcta)`.

---

## Flujo de estado de un intento

```
[INICIO]
  POST /api/exams/start
    → Crea intentos_examen (finalizado_at=NULL)
    → Crea N filas en respuestas_intento (opcion_seleccionada=NULL)
    → Retorna attempt_id + primera pregunta (orden=1)

[POR CADA PREGUNTA]
  POST /api/exams/{id}/answer
    → Actualiza respuestas_intento para el orden actual
    → Retorna siguiente pregunta o señal de finalización

[TIMER AGOTADO - cliente]
  POST /api/exams/{id}/answer con { opcion_seleccionada: null, tiempo_agotado: true }
    → Misma lógica que respuesta normal

[FIN]
  POST /api/exams/{id}/finish (o automático tras última pregunta)
    → Calcula puntuacion y resultado en intentos_examen
    → Establece finalizado_at = NOW()
    → Retorna resumen de resultados

[CONSULTA]
  GET /api/exams/{id}/results
    → Retorna todas las respuestas con feedback visual y fundamento_juridico
```
