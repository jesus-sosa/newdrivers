# Guía de Validación: Simulador de Examen de Manejo

**Feature**: 001-exam-simulator
**Date**: 2026-06-17
**Propósito**: Verificar que el sistema funciona correctamente de extremo a extremo.
Esta guía es de validación, no de implementación. Los comandos asumen el entorno de desarrollo.

---

## Prerrequisitos

- Docker y Docker Compose v2 instalados
- Variables de entorno configuradas en `.env` (ver `.env.example`)
- Banco de preguntas CSV disponible en `backend/static/data/banco_preguntas.csv`
- Imágenes de señales disponibles en `backend/static/imagenes_senales/`

---

## Setup: Levantar el entorno de desarrollo

```bash
# Desde la raíz del repo newdrivers-exams
docker compose up -d

# Verificar que los servicios están corriendo
docker compose ps
# Esperado: backend (healthy), frontend (healthy), db (healthy)

# Ejecutar migraciones
docker compose exec backend alembic upgrade head

# Importar banco de preguntas inicial
curl -X POST http://localhost:8000/api/questions/import \
  -H "Authorization: Bearer <admin_token>" \
  -F "file=@backend/static/data/banco_preguntas.csv"
# Esperado: { "insertadas": 62, "actualizadas": 0, "errores": [] }
```

---

## Escenario 1: Registro y acceso de estudiante (US2)

```bash
# 1. Registrar nuevo estudiante
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nombre_completo": "Test Estudiante", "email": "test@newdrivers.com", "password": "Test1234!"}'
# Esperado: 201 Created, rol="estudiante"

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@newdrivers.com", "password": "Test1234!"}'
# Esperado: 200 OK, access_token presente

# 3. Verificar que el estudiante NO puede acceder a configuración
curl -X GET http://localhost:8000/api/admin/config \
  -H "Authorization: Bearer <student_token>"
# Esperado: 403 Forbidden
```

---

## Escenario 2: Configuración del sistema por admin (US4)

```bash
# 1. Intentar iniciar examen SIN porcentaje_aprobacion configurado
curl -X POST http://localhost:8000/api/exams/start \
  -H "Authorization: Bearer <student_token>"
# Esperado: 409 Conflict — "sistema no configurado"

# 2. Admin configura el sistema
curl -X PUT http://localhost:8000/api/admin/config \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"num_preguntas": 20, "segundos_por_pregunta": 60, "porcentaje_aprobacion": 70.0}'
# Esperado: 200 OK, estado_sistema="activo"

# 3. Verificar que Editor NO puede acceder a configuración
curl -X GET http://localhost:8000/api/admin/config \
  -H "Authorization: Bearer <editor_token>"
# Esperado: 403 Forbidden
```

---

## Escenario 3: Flujo completo de examen (US1 — camino feliz)

```bash
# 1. Estudiante inicia examen
curl -X POST http://localhost:8000/api/exams/start \
  -H "Authorization: Bearer <student_token>"
# Esperado: 201 Created, attempt_id presente, pregunta_actual con opciones A/B/C/D
# Verificar: imagen_archivo y fundamento_juridico NO aparecen en la respuesta

# 2. Responder pregunta 1 correctamente
curl -X POST http://localhost:8000/api/exams/{attempt_id}/answer \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"orden": 1, "opcion_seleccionada": "<correcta>", "tiempo_agotado": false}'
# Esperado: 200 OK, siguiente_pregunta con orden=2

# 3. Simular tiempo agotado en pregunta 2
curl -X POST http://localhost:8000/api/exams/{attempt_id}/answer \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"orden": 2, "opcion_seleccionada": null, "tiempo_agotado": true}'
# Esperado: 200 OK, siguiente_pregunta con orden=3

# 4. Responder las preguntas restantes (3–20) y verificar finalización automática
# Al responder la pregunta 20, la respuesta incluye:
# Esperado: examen_finalizado=true, resumen con puntuacion y resultado

# 5. Consultar resultados completos
curl -X GET http://localhost:8000/api/exams/{attempt_id}/results \
  -H "Authorization: Bearer <student_token>"
# Esperado:
#   - pregunta respondida correctamente → es_correcta=true, respuesta_correcta visible
#   - pregunta con tiempo agotado → tiempo_agotado=true, es_correcta=false, respuesta_correcta visible
#   - fundamento_juridico visible para todas las preguntas
```

---

## Escenario 4: Reconexión durante examen (caso borde)

```bash
# 1. Iniciar examen y responder 5 preguntas
# 2. Simular pérdida de conexión (cerrar ventana)
# 3. Reconectarse y recuperar estado
curl -X GET http://localhost:8000/api/exams/{attempt_id} \
  -H "Authorization: Bearer <student_token>"
# Esperado: estado="en_curso", pregunta_actual con orden=6, respondidas=5
```

---

## Escenario 5: Gestión del banco de preguntas (US3)

```bash
# 1. Editor crea una pregunta nueva
curl -X POST http://localhost:8000/api/questions \
  -H "Authorization: Bearer <editor_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tema": "Responsabilidad vial",
    "pregunta": "¿Cuál es la distancia mínima de seguimiento?",
    "opcion_a": "3 metros",
    "opcion_b": "5 metros",
    "opcion_c": "La distancia necesaria para frenar",
    "opcion_d": "10 metros",
    "respuesta_correcta": "C"
  }'
# Esperado: 201 Created

# 2. Verificar que aparece en el listado filtrado por tema
curl "http://localhost:8000/api/questions?tema=Responsabilidad+vial" \
  -H "Authorization: Bearer <editor_token>"
# Esperado: la nueva pregunta aparece en el listado

# 3. Soft-delete de la pregunta
curl -X DELETE http://localhost:8000/api/questions/{id} \
  -H "Authorization: Bearer <editor_token>"
# Esperado: 204 No Content

# 4. Verificar que no aparece en el banco activo
curl "http://localhost:8000/api/questions?activa=true" \
  -H "Authorization: Bearer <editor_token>"
# Esperado: la pregunta no aparece
```

---

## Escenario 6: Gestión de estudiantes (US5)

```bash
# Editor agrega un estudiante
curl -X POST http://localhost:8000/api/admin/students \
  -H "Authorization: Bearer <editor_token>" \
  -H "Content-Type: application/json" \
  -d '{"nombre_completo": "Nuevo Alumno", "email": "alumno@newdrivers.com", "password": "Temp1234!"}'
# Esperado: 201 Created, rol="estudiante"

# Verificar que el nuevo estudiante puede iniciar sesión
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alumno@newdrivers.com", "password": "Temp1234!"}'
# Esperado: 200 OK con access_token
```

---

## Ejecución de tests automatizados

```bash
# Tests backend completos
docker compose exec backend pytest tests/ -v

# Solo tests de integración
docker compose exec backend pytest tests/integration/ -v

# Solo tests de contrato
docker compose exec backend pytest tests/contract/ -v

# Tests frontend
docker compose exec frontend npm run test
```

**Criterios de éxito de los tests**:
- 0 tests fallidos en todos los suites
- Cobertura de endpoints: 100% de rutas definidas en contracts/
- Tests de contrato validan RBAC: cada rol solo accede a lo que le corresponde

---

## Verificación de criterios de éxito (CE)

| Criterio | Cómo verificar |
|----------|----------------|
| CE-001: examen completo < 30 min | Registrarse + completar 20 preguntas → medir tiempo total |
| CE-002: sin preguntas repetidas | Revisar `respuestas_intento` — no hay `pregunta_id` duplicado por intento |
| CE-003: resultado en < 3 s | Medir tiempo entre `POST /finish` y respuesta |
| CE-004: 100% intentos guardados | Verificar `GET /history` tras cada intento |
| CE-005: config refleja en siguiente examen | Cambiar `num_preguntas` → iniciar examen → verificar total en respuesta |
| CE-006: pregunta disponible en < 1 min | Crear pregunta → `GET /questions` → verificar presencia |
| CE-007: RBAC 100% efectivo | Ejecutar escenarios 1 y 2 de esta guía |
