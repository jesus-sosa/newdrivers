# Research: Simulador de Examen de Manejo

**Feature**: 001-exam-simulator
**Date**: 2026-06-17

---

## 1. Temporizador por pregunta: estrategia client-side vs server-side

**Decisión**: Temporizador client-side con validación server-side pasiva.

**Justificación**:
- El timer se ejecuta en el navegador (composable `useTimer.ts`) para UX fluida sin latencia.
- Al agotar el tiempo, el cliente envía automáticamente `{ opcion_seleccionada: null, tiempo_agotado: true }`.
- El servidor registra `respondida_at` al recibir la respuesta; no valida la duración exacta
  (aceptable para un simulador educativo, no un examen oficial).
- Si el cliente pierde conexión, el intento queda en estado `iniciado`; al reconectarse el
  frontend recupera el estado desde `GET /api/exams/{id}` y retoma desde la última pregunta
  pendiente.

**Alternativas descartadas**:
- Timer 100% server-side (WebSockets): complejidad innecesaria para este caso de uso educativo.
- Validación estricta del tiempo en servidor: overhead sin beneficio real en simulador.

---

## 2. Selección aleatoria de preguntas

**Decisión**: Shuffle en aplicación (Fisher-Yates) sobre el conjunto de preguntas activas.

**Justificación**:
- Al iniciar un examen, el servicio carga todas las preguntas activas de la BD, aplica
  Fisher-Yates y toma los primeros N (número configurado).
- El resultado se persiste inmediatamente en `respuestas_intento` con su campo `orden`, de
  modo que el examen es reproducible en caso de reconexión.
- Evita `ORDER BY RANDOM()` de PostgreSQL que no es reproducible entre llamadas.

**Alternativas descartadas**:
- `ORDER BY RANDOM() LIMIT N` en BD: no reproducible; problemático para reconexión y revisión.
- Pre-calcular exámenes: innecesario para el volumen de uso esperado.

---

## 3. Almacenamiento y servicio de imágenes de preguntas

**Decisión**: Imágenes almacenadas en volumen Docker montado; servidas por Nginx en producción
y por FastAPI (`StaticFiles`) en desarrollo.

**Justificación**:
- El banco de preguntas existente ya tiene rutas relativas en `imagen_archivo`
  (ej. `imagenes_senales/pg04_img03_184x81.jpeg`).
- Las imágenes se montan en `/opt/newdrivers/newdrivers-exams/static/` y se sirven bajo
  `/static/` en la URL pública.
- En desarrollo: `app.mount("/static", StaticFiles(directory="static"), name="static")`.
- En producción: Nginx sirve `/static/` directamente desde el volumen, sin pasar por el backend.

**Alternativas descartadas**:
- S3/Object storage: costo y complejidad innecesarios para el volumen actual de imágenes.
- Base64 en BD: aumenta el tamaño de las filas y penaliza las consultas.

---

## 4. Estructura JWT y gestión de sesión

**Decisión**: Access token (30 min) + Refresh token (7 días) en cookie httpOnly.

**Justificación**:
- Access token contiene: `{ sub: user_id, email, rol, exp }`.
- Refresh token se almacena en cookie httpOnly (no accesible por JavaScript, mitiga XSS).
- El frontend gestiona el refresh automático antes de que expire el access token.
- Secret de firma: variable de entorno `JWT_SECRET_KEY`, mínimo 256 bits.

**Alternativas descartadas**:
- Solo access token sin refresh: el estudiante pierde el examen si el token expira durante el mismo.
- localStorage para tokens: vulnerable a XSS.

---

## 5. RBAC: implementación en FastAPI

**Decisión**: Dependency injection con función `require_roles(roles: list[str])`.

**Justificación**:
- Cada router declara sus dependencias: `Depends(require_roles(["admin", "editor"]))`.
- La dependencia extrae el rol del JWT y lanza `HTTP 403` si no coincide.
- La autorización es a nivel de endpoint (Principio IV de la constitución), no solo en middleware
  global.

**Alternativas descartadas**:
- Middleware global: no permite granularidad por endpoint.
- Decoradores custom: menos idiomático en FastAPI que Depends.

---

## 6. Compatibilidad con el banco de preguntas existente

**Decisión**: Reutilizar el esquema provisto con adiciones mínimas.

**Justificación**:
- El DDL existente (`preguntas_licencia`) se adopta como base con dos adiciones:
  - Campo `activa BOOLEAN DEFAULT true` para soft-delete (RF-008: preguntas en exámenes activos
    no se pueden eliminar definitivamente).
  - Campo `updated_at TIMESTAMPTZ` para auditoría.
- El import masivo lee el CSV y hace `INSERT ... ON CONFLICT DO NOTHING`.
- Las imágenes referenciadas en `imagen_archivo` se copian al volumen estático durante el setup.

---

## 7. Estado de un intento de examen

**Decisión**: Máquina de estados simple con campo `finalizado_at`.

| Estado | Condición |
|--------|-----------|
| `iniciado` | `finalizado_at IS NULL` |
| `finalizado` | `finalizado_at IS NOT NULL` |

- Un intento iniciado pero sin actividad por más de (num_preguntas × segundos_por_pregunta + 60s)
  se considera abandonado; al retomarlo el frontend detecta que no quedan preguntas pendientes
  y llama a `POST /api/exams/{id}/finish` automáticamente.
- No se implementa un estado `abandonado` explícito en v1 (YAGNI).

---

## 8. Configuración del sistema: singleton

**Decisión**: Tabla `configuracion_examen` con una única fila (id=1).

**Justificación**:
- Simplicidad total: `GET /api/admin/config` siempre lee id=1; `PUT` hace upsert.
- El sistema bloquea el inicio de exámenes si `porcentaje_aprobacion IS NULL`.
- Alternativas (tabla de clave-valor, archivo de configuración) añaden complejidad sin beneficio.

---

## 9. Importación masiva del banco de preguntas

**Decisión**: Endpoint `POST /api/questions/import` que acepta archivo CSV (multipart/form-data).

**Justificación**:
- El CSV de muestra tiene la estructura exacta del DDL provisto.
- El endpoint valida cabeceras, convierte encoding (el CSV tiene problemas de UTF-8 con latin1),
  hace insert con `ON CONFLICT (id) DO UPDATE` para re-importaciones idempotentes.
- Solo accesible para roles `admin` y `editor`.
- Las imágenes referenciadas deben subirse separadamente al volumen estático.

---

## 10. Nuxt 3 + Pinia para estado del examen

**Decisión**: Store `exam.ts` en Pinia gestiona el estado del examen activo en el cliente.

**Justificación**:
- La pregunta actual, el progreso y el estado del timer viven en el store para ser accesibles
  desde el componente de timer y el componente de pregunta sin prop drilling.
- Al navegar accidentalmente fuera del examen, el store conserva el estado hasta que el
  componente de examen detecta que el `attempt_id` sigue activo en el servidor.
- El store se hidrata desde `GET /api/exams/{id}` al montar la página del examen.
