---

description: "Lista de tareas para implementación del Simulador de Examen de Manejo"
---

# Tasks: Simulador de Examen de Manejo

**Input**: Documentos de diseño en `specs/001-exam-simulator/`

**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅

**Tests**: Incluidos — la constitución del proyecto los hace OBLIGATORIOS (Principio III).
El ciclo es: escribir test → verificar que falla → implementar → verificar que pasa.

**Organización**: Tareas agrupadas por historia de usuario para habilitar entrega incremental.

## Formato: `[ID] [P?] [Story?] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias bloqueantes)
- **[Story]**: Historia de usuario a la que pertenece (US1–US6)
- Todas las tareas incluyen ruta exacta de archivo

## Convenciones de rutas

```
backend/app/models/        # SQLModel models
backend/app/services/      # Business logic
backend/app/routers/       # FastAPI routers
backend/app/core/          # Config, DB, JWT, RBAC
backend/alembic/versions/  # DB migrations
backend/tests/unit/        # Pruebas unitarias
backend/tests/integration/ # Pruebas de integración vs BD real
backend/tests/contract/    # Pruebas de contrato entre módulos
frontend/components/       # Componentes Vue reutilizables
frontend/pages/            # Páginas Nuxt (file-based routing)
frontend/composables/      # Composables Vue 3
frontend/stores/           # Pinia stores
frontend/layouts/          # Layouts Nuxt
frontend/tests/            # Pruebas Vitest
```

---

## Phase 1: Setup (Estructura e inicialización)

**Propósito**: Crear la estructura del repositorio y configurar las herramientas base.

- [ ] T001 Crear estructura de directorios del repositorio: `backend/`, `frontend/`, `backend/app/`, `backend/tests/`, `frontend/components/`, `frontend/pages/`, `frontend/composables/`, `frontend/stores/`, `frontend/layouts/`, `frontend/tests/`
- [ ] T002 [P] Inicializar proyecto Python backend con `pyproject.toml` y `requirements.txt` (fastapi, sqlmodel, alembic, python-jose[cryptography], passlib[bcrypt], python-multipart, httpx, pytest, pytest-asyncio)
- [ ] T003 [P] Inicializar proyecto Nuxt 3 frontend con `package.json` (nuxt@3, pinia, @pinia/nuxt, vitest, @nuxt/test-utils, @nuxtjs/eslint-config)
- [ ] T004 Crear `docker-compose.yml` con servicios: `backend` (port 8000), `frontend` (port 3000), `db` (PostgreSQL 15, port 5432 solo interno), red interna `exams-net`, red externa `nginx-proxy-net` y `db-net`
- [ ] T005 [P] Crear `docker-compose.prod.yml` con servicios: `backend` y `frontend` únicamente (sin `db` local; usa BD de `newdrivers-infra` vía env var)
- [ ] T006 [P] Crear `backend/Dockerfile` (imagen Python 3.11-slim, instala deps, copia app, CMD uvicorn)
- [ ] T007 [P] Crear `frontend/Dockerfile` (imagen Node 20-alpine, `npm run build`, CMD node .output/server/index.mjs)
- [ ] T008 [P] Crear `.env.example` con todas las variables requeridas: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `CORS_ORIGINS`, `NUXT_PUBLIC_API_BASE`
- [ ] T009 [P] Crear `cloudbuild.yaml` con pasos: test backend, test frontend, build images, push to registry, deploy via SSH to Lightsail
- [ ] T010 [P] Configurar `ruff`, `black` y `mypy` en `backend/pyproject.toml` (linting y type checking)
- [ ] T011 [P] Configurar ESLint y Prettier para el frontend en `frontend/.eslintrc` y `frontend/.prettierrc`
- [ ] T012 [P] Configurar Nuxt en `frontend/nuxt.config.ts` (runtimeConfig con `apiBase`, módulos: `@pinia/nuxt`)

---

## Phase 2: Foundational (Infraestructura bloqueante)

**Propósito**: Core técnico que todas las historias de usuario requieren.

**⚠️ CRÍTICO**: Ninguna historia puede comenzar hasta completar esta fase.

- [ ] T013 Crear `backend/app/core/settings.py` — Pydantic `Settings` leyendo todas las variables de entorno del `.env.example`
- [ ] T014 [P] Crear `backend/app/core/database.py` — SQLModel engine, `get_session` dependency, `create_db_and_tables()`
- [ ] T015 [P] Crear `backend/app/core/security.py` — `create_access_token()`, `create_refresh_token()`, `verify_token()`, `hash_password()`, `verify_password()` usando `python-jose` y `passlib`
- [ ] T016 Crear `backend/app/core/dependencies.py` — `get_current_user()` dependency (extrae JWT del header), `require_roles(roles: list[str])` factory que devuelve dependency y lanza HTTP 403 si el rol no coincide
- [ ] T017 [P] Crear `backend/app/models/user.py` — SQLModel `User` con todos los campos de `data-model.md`: `id` (UUID), `nombre_completo`, `email` (unique), `password_hash`, `rol` (enum: admin/editor/estudiante), `activo`, `created_at`, `updated_at`
- [ ] T018 [P] Crear `backend/app/models/pregunta.py` — SQLModel `Pregunta` con todos los campos de `data-model.md`: `id` (SERIAL), `tema`, `pregunta`, `imagen_archivo`, `descripcion_imagen`, `opcion_a`, `opcion_b`, `opcion_c`, `opcion_d`, `respuesta_correcta` (CHAR check A/B/C/D), `fundamento_juridico`, `activa`, `created_at`, `updated_at`
- [ ] T019 [P] Crear `backend/app/models/config.py` — SQLModel `ConfiguracionExamen` singleton (id=1 enforced): `num_preguntas`, `segundos_por_pregunta`, `porcentaje_aprobacion` (nullable), `updated_at`, `updated_by` (FK → users)
- [ ] T020 Crear `backend/app/models/intento.py` — SQLModel `IntentoExamen`: `id` (UUID), `estudiante_id` (FK → users), `num_preguntas` (snapshot), `porcentaje_aprobacion` (snapshot), `puntuacion`, `resultado` (enum: aprobado/reprobado), `iniciado_at`, `finalizado_at`
- [ ] T021 Crear `backend/app/models/respuesta.py` — SQLModel `RespuestaIntento`: `id` (UUID), `intento_id` (FK → intentos_examen), `pregunta_id` (FK → preguntas), `orden`, `opcion_seleccionada` (nullable CHAR A/B/C/D), `es_correcta` (nullable bool), `tiempo_agotado` (bool default false), `respondida_at`; unique constraint en `(intento_id, pregunta_id)` y `(intento_id, orden)`
- [ ] T022 Crear migración Alembic inicial en `backend/alembic/versions/001_initial_schema.py` — crea las 5 tablas con todos sus índices y constraints del `data-model.md`; inserta fila singleton en `configuracion_examen` con `id=1`, valores por defecto, `porcentaje_aprobacion=NULL`
- [ ] T023 Crear `backend/app/main.py` — instancia FastAPI, configura CORS desde settings, monta `StaticFiles` en `/static`, incluye todos los routers (prefijo `/api`), registra manejador global de errores HTTP
- [ ] T024 Crear `backend/app/services/auth_service.py` — método `login(email, password, session)`: busca usuario activo por email, verifica password, retorna access + refresh tokens; método `get_user_by_id(user_id, session)` para dependency
- [ ] T025 Crear `backend/app/routers/auth.py` — endpoints: `POST /login`, `POST /refresh` (lee cookie httpOnly), `POST /logout` (borra cookie), `GET /me` (requiere JWT); establece/elimina cookie httpOnly para refresh token
- [ ] T026 [P] Crear `backend/tests/conftest.py` — fixtures: `test_db` (BD PostgreSQL de test limpia por función), `client` (TestClient con `test_db`), `admin_token`, `editor_token`, `student_token` (crean usuarios de test y retornan JWT)
- [ ] T027 [P] Crear `backend/app/core/seeder.py` — script que crea usuario admin inicial si no existe (lee credenciales desde env vars `ADMIN_EMAIL`, `ADMIN_PASSWORD`); ejecutable con `python -m app.core.seeder`
- [ ] T028 [P] Crear `frontend/middleware/auth.ts` — Nuxt route middleware: redirige a `/login` si no hay token en el auth store; redirige a `/` si rol `estudiante` intenta acceder a `/admin`
- [ ] T029 [P] Crear `frontend/stores/auth.ts` — Pinia store: `user`, `accessToken`; actions: `login()`, `logout()`, `refresh()`, `fetchMe()`; persiste token en cookie segura del cliente
- [ ] T030 [P] Crear `frontend/composables/useAuth.ts` — composable que expone `login()`, `logout()`, `register()` llamando al API y actualizando el auth store
- [ ] T031 [P] Crear `frontend/layouts/default.vue` — layout para estudiantes: navbar con logo New Drivers, enlace a historial, botón de logout
- [ ] T032 [P] Crear `frontend/layouts/admin.vue` — layout para admin/editor: sidebar con navegación a Banco de preguntas, Estudiantes, Configuración (esta última visible solo para admin); navbar superior con logo
- [ ] T033 [P] Crear `frontend/pages/admin/index.vue` — dashboard landing para admin/editor: contadores (total preguntas, total estudiantes, config status)

**Checkpoint**: Fundación lista — las historias de usuario pueden comenzar

---

## Phase 3: US1 — Estudiante realiza un examen simulador (Prioridad: P1) 🎯 MVP

**Goal**: Un estudiante autenticado puede iniciar un examen, responder preguntas con timer de 60s por pregunta, ver retroalimentación visual y fundamento legal en resultados.

**Independent Test**: Iniciar sesión como estudiante → `POST /api/exams/start` → responder 20 preguntas (incluyendo una con timer agotado) → `GET /api/exams/{id}/results` → verificar score, colores y fundamentos.

### Tests para US1 ⚠️ Escribir PRIMERO — verificar que fallan antes de implementar

- [ ] T034 [P] [US1] Escribir test de integración `test_start_exam_success` en `backend/tests/integration/test_exams.py` — verifica: 201, `attempt_id` presente, `pregunta_actual` con 4 opciones sin `respuesta_correcta`, `segundos_por_pregunta` en respuesta
- [ ] T035 [P] [US1] Escribir test de integración `test_start_exam_no_config` en `backend/tests/integration/test_exams.py` — verifica: 409 cuando `porcentaje_aprobacion IS NULL`
- [ ] T036 [P] [US1] Escribir test de integración `test_answer_question_correct` y `test_answer_timeout` en `backend/tests/integration/test_exams.py` — verifica registro de respuesta correcta e incorrecta por timeout
- [ ] T037 [P] [US1] Escribir test de integración `test_get_results_after_finish` en `backend/tests/integration/test_exams.py` — verifica: `respuesta_correcta` visible en resultados, `fundamento_juridico` presente, colores inferibles (es_correcta, tiempo_agotado)
- [ ] T038 [P] [US1] Escribir unit test `test_fisher_yates_no_repeats` en `backend/tests/unit/test_exam_service.py` — verifica que shuffle no repite preguntas en mismo intento
- [ ] T039 [P] [US1] Escribir unit test `test_score_calculation` en `backend/tests/unit/test_exam_service.py` — verifica cálculo de puntuación y resultado aprobado/reprobado según porcentaje

### Implementación US1

- [ ] T040 [US1] Crear `backend/app/services/exam_service.py` con métodos: `start_exam(student_id, session)` (valida config, Fisher-Yates shuffle, crea `intentos_examen` + N filas `respuestas_intento`), `get_exam_state(attempt_id, student_id, session)`, `submit_answer(attempt_id, orden, opcion, tiempo_agotado, session)` (valida orden, calcula `es_correcta`, retorna siguiente pregunta o señal de fin), `finish_exam(attempt_id, session)` (calcula score, resultado, establece `finalizado_at`), `get_results(attempt_id, session)` (retorna todas las respuestas con feedback + `fundamento_juridico`), `get_history(student_id, page, page_size, session)`
- [ ] T041 [US1] Crear `backend/app/routers/exams.py` — todos los endpoints del contrato `contracts/exams-api.md`: `POST /start`, `GET /{id}`, `POST /{id}/answer`, `POST /{id}/finish`, `GET /{id}/results`, `GET /history`; aplica `require_roles(["estudiante"])` en start/answer/finish; `GET /{id}/results` permite también `admin`
- [ ] T042 [P] [US1] Crear `frontend/composables/useTimer.ts` — composable: `startTimer(seconds, onExpire)`, `stopTimer()`, `timeLeft` (ref reactivo); usa `setInterval`; llama `onExpire()` cuando llega a 0
- [ ] T043 [P] [US1] Crear `frontend/composables/useExam.ts` — composable: `startExam()` (llama API, guarda en store), `submitAnswer(orden, opcion, tiempoAgotado)` (llama API, avanza pregunta o navega a resultados), `loadExamState(attemptId)` (reconexión)
- [ ] T044 [P] [US1] Crear `frontend/stores/exam.ts` — Pinia store: `attemptId`, `currentQuestion`, `totalPreguntas`, `respondidas`, `segundosPorPregunta`, `estado`; actions: `setCurrentQuestion()`, `incrementProgress()`, `reset()`
- [ ] T045 [P] [US1] Crear `frontend/components/exam/TimerBar.vue` — barra de progreso visual del timer: prop `seconds` (total), prop `timeLeft` (actual); color verde → amarillo → rojo según % restante; emite `expire` cuando llega a 0
- [ ] T046 [P] [US1] Crear `frontend/components/exam/ProgressBar.vue` — barra de progreso del examen: prop `current` (pregunta actual), prop `total` (total preguntas); muestra "Pregunta N de M"
- [ ] T047 [P] [US1] Crear `frontend/components/exam/AnswerOption.vue` — opción de respuesta seleccionable: props `letra` (A/B/C/D), `texto`, `seleccionada` (bool), `deshabilitada` (bool); emite `select` al hacer click; estilo destacado en azul cuando seleccionada
- [ ] T048 [US1] Crear `frontend/components/exam/QuestionCard.vue` — card de pregunta completa: props `pregunta` (objeto), `orden`, `total`; muestra imagen de apoyo si `imagen_archivo` existe (usando `/static/` como base URL); renderiza 4 `AnswerOption`; integra `TimerBar` y `ProgressBar`; emite `answer(opcion)` y maneja `timerExpire` enviando respuesta vacía
- [ ] T049 [US1] Crear `frontend/pages/exam/[id].vue` — página de examen activo: carga estado del examen al montar (usa `useExam.loadExamState`), inicia timer por pregunta, renderiza `QuestionCard`, maneja avance automático al expirar timer, navega a `/exam/[id]/results` al finalizar; redirige a `/` si intento ya finalizado
- [ ] T050 [P] [US1] Crear `frontend/components/results/ScoreCard.vue` — card de resultado final: props `puntuacion`, `totalPreguntas`, `resultado` (aprobado/reprobado); muestra "X de N correctas", texto y emoji de aprobado/reprobado; botón "Intentar de nuevo" que navega a `/`
- [ ] T051 [P] [US1] Crear `frontend/components/results/LegalBasisBlock.vue` — bloque de fundamento legal: prop `texto`; renderizado en sección colapsable bajo cada pregunta revisada
- [ ] T052 [P] [US1] Crear `frontend/components/results/QuestionReview.vue` — revisión de una pregunta: props `pregunta` (objeto con todas las opciones, respuesta correcta, es_correcta, tiempo_agotado, opcion_seleccionada); muestra opción correcta en verde, opción seleccionada incorrecta en rojo, preguntas sin respuesta (tiempo agotado) con indicador gris + respuesta correcta destacada; incluye `LegalBasisBlock`
- [ ] T053 [US1] Crear `frontend/pages/exam/[id]/results.vue` — página de resultados: carga `GET /api/exams/{id}/results`, renderiza `ScoreCard` en cabecera, lista todas las preguntas con `QuestionReview`; solo accesible si `finalizado_at IS NOT NULL`
- [ ] T054 [US1] Crear `frontend/pages/index.vue` — dashboard del estudiante: muestra botón "Iniciar Examen" (llama `POST /api/exams/start` y navega a `/exam/{id}`); muestra aviso si el sistema no está configurado (porcentaje_aprobacion = null); muestra últimos 3 intentos del historial
- [ ] T055 [P] [US1] Escribir Vitest test para `TimerBar.vue` en `frontend/tests/components/exam/TimerBar.test.ts` — verifica: renderiza timeLeft, aplica clase de color correcto, emite `expire` al llegar a 0
- [ ] T056 [P] [US1] Escribir Vitest test para `AnswerOption.vue` en `frontend/tests/components/exam/AnswerOption.test.ts` — verifica: emite `select` al click, aplica estilo cuando `seleccionada=true`, no emite cuando `deshabilitada=true`
- [ ] T057 [P] [US1] Escribir Vitest test para `useTimer.ts` en `frontend/tests/composables/useTimer.test.ts` — verifica: `timeLeft` decrementa por segundo, `onExpire` se llama al llegar a 0, `stopTimer` detiene el countdown

**Checkpoint**: US1 lista — estudiante puede tomar examen completo e ver resultados con retroalimentación

---

## Phase 4: US2 — Nuevo estudiante se registra (Prioridad: P2)

**Goal**: Un usuario nuevo puede crear su cuenta como estudiante y acceder al simulador.

**Independent Test**: `POST /api/auth/register` con datos válidos → 201 → `POST /api/auth/login` → 200 con token → `GET /api/auth/me` → rol=estudiante.

### Tests para US2 ⚠️ Escribir PRIMERO

- [ ] T058 [P] [US2] Escribir test de integración `test_register_success` en `backend/tests/integration/test_auth.py` — verifica: 201, `rol="estudiante"`, contraseña no devuelta en respuesta
- [ ] T059 [P] [US2] Escribir test de integración `test_register_duplicate_email` en `backend/tests/integration/test_auth.py` — verifica: 409 al registrar email ya existente

### Implementación US2

- [ ] T060 [P] [US2] Agregar método `register(nombre, email, password, session)` a `backend/app/services/auth_service.py` — verifica unicidad de email (409 si duplicado), hashea password con bcrypt, crea usuario con `rol=estudiante`
- [ ] T061 [US2] Agregar endpoint `POST /register` al router en `backend/app/routers/auth.py` — público (sin JWT); llama `auth_service.register()`; retorna 201 con datos del usuario (sin password_hash)
- [ ] T062 [P] [US2] Crear `frontend/pages/login.vue` — formulario email + contraseña; llama `useAuth().login()`; redirige a `/` si es estudiante o a `/admin` si es admin/editor; muestra link a `/register`
- [ ] T063 [US2] Crear `frontend/pages/register.vue` — formulario nombre + email + contraseña; llama `useAuth().register()`; redirige a `/login` tras éxito; muestra link a `/login`
- [ ] T064 [P] [US2] Escribir Vitest test para validación de formulario en `frontend/tests/pages/login.test.ts` — verifica: error visible si email vacío, error si contraseña < 8 chars, no llama API con datos inválidos

**Checkpoint**: US2 lista — estudiante puede registrarse de forma autónoma e inmediatamente tomar examen

---

## Phase 5: US3 — Admin y Editor gestionan banco de preguntas (Prioridad: P3)

**Goal**: Admin y editor pueden crear, editar, eliminar y filtrar preguntas; importar banco inicial desde CSV.

**Independent Test**: Crear pregunta vía `POST /api/questions` → `GET /api/questions?tema=X` → verificar que aparece → `DELETE /api/questions/{id}` → verificar que `activa=false` en listado.

### Tests para US3 ⚠️ Escribir PRIMERO

- [ ] T065 [P] [US3] Escribir test de integración `test_list_questions_with_filters` en `backend/tests/integration/test_questions.py` — verifica paginación, filtro por `tema`, filtro por `activa`
- [ ] T066 [P] [US3] Escribir test de integración `test_create_question_validation` en `backend/tests/integration/test_questions.py` — verifica: 201 con datos válidos, 400 si `respuesta_correcta` no es A/B/C/D
- [ ] T067 [P] [US3] Escribir test de integración `test_soft_delete_question` en `backend/tests/integration/test_questions.py` — verifica: 204, pregunta no aparece en `GET ?activa=true`, pero sí en `GET ?activa=false`
- [ ] T068 [P] [US3] Escribir test de integración `test_import_csv` en `backend/tests/integration/test_questions.py` — verifica: upload de CSV de muestra, respuesta con contadores correctos, preguntas disponibles en banco
- [ ] T069 [P] [US3] Escribir unit test `test_rbac_editor_cannot_access_config` en `backend/tests/unit/test_rbac.py` — verifica que `require_roles(["admin"])` lanza 403 cuando se pasa token de editor

### Implementación US3

- [ ] T070 [US3] Crear `backend/app/services/question_service.py` con métodos: `list_questions(tema, activa, q, page, page_size, session)`, `create_question(data, session)`, `get_question(id, session)`, `update_question(id, data, session)` (verifica no hay intento activo antes de cambiar respuesta_correcta), `soft_delete(id, session)` (verifica no hay intento activo), `import_csv(file_content, session)` (parsea CSV, upsert por id, retorna estadísticas), `list_temas(session)`
- [ ] T071 [US3] Crear `backend/app/routers/questions.py` — todos los endpoints del contrato `contracts/questions-api.md`: `GET /`, `POST /`, `GET /temas`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, `POST /import`; aplica `require_roles(["admin", "editor"])` en todos
- [ ] T072 [P] [US3] Crear `frontend/components/admin/QuestionForm.vue` — formulario de pregunta: campos tema (select con temas disponibles), pregunta (textarea), opciones A/B/C/D (text inputs), selector de respuesta correcta (radio A/B/C/D), imagen_archivo (text input para ruta), descripcion_imagen (text input), fundamento_juridico (textarea); emite `submit(data)` y `cancel`
- [ ] T073 [P] [US3] Crear `frontend/components/admin/ImportForm.vue` — componente de importación CSV: input file, botón upload, muestra resultado (insertadas/actualizadas/errores) tras respuesta del API
- [ ] T074 [US3] Crear `frontend/pages/admin/questions/index.vue` — listado del banco: tabla paginada con columnas (ID, tema, pregunta truncada, activa, acciones); filtros por tema y búsqueda libre; botones "Nueva pregunta" e "Importar CSV"; modal de confirmación para eliminar
- [ ] T075 [P] [US3] Crear `frontend/pages/admin/questions/new.vue` — formulario para crear nueva pregunta usando `QuestionForm.vue`; llama `POST /api/questions`; redirige a `/admin/questions` tras éxito
- [ ] T076 [P] [US3] Crear `frontend/pages/admin/questions/[id]/edit.vue` — formulario para editar pregunta: carga pregunta con `GET /api/questions/{id}`, muestra `QuestionForm` pre-cargado; llama `PUT /api/questions/{id}`; redirige a `/admin/questions` tras éxito

**Checkpoint**: US3 lista — banco de preguntas completamente gestionable

---

## Phase 6: US4 — Admin configura parámetros del examen (Prioridad: P4)

**Goal**: Admin puede definir número de preguntas, timer por pregunta y porcentaje de aprobación. Editor no puede acceder a esta sección.

**Independent Test**: Admin `PUT /api/admin/config` con `num_preguntas=10, porcentaje_aprobacion=80` → estudiante `POST /api/exams/start` → examen tiene 10 preguntas → resultado calificado con 80%.

### Tests para US4 ⚠️ Escribir PRIMERO

- [ ] T077 [P] [US4] Escribir test de integración `test_get_config_admin_only` en `backend/tests/integration/test_admin.py` — verifica: 200 para admin, 403 para editor, 403 para estudiante
- [ ] T078 [P] [US4] Escribir test de integración `test_update_config_validation` en `backend/tests/integration/test_admin.py` — verifica: 200 con datos válidos, 400 si `num_preguntas` > preguntas activas en banco, 400 si `porcentaje_aprobacion` > 100
- [ ] T079 [P] [US4] Escribir test de integración `test_config_snapshot_isolation` en `backend/tests/integration/test_admin.py` — verifica que cambiar config no afecta intentos ya iniciados (snapshot guardado en `intentos_examen`)

### Implementación US4

- [ ] T080 [US4] Crear `backend/app/services/admin_service.py` con métodos: `get_config(session)`, `update_config(data, updated_by_id, session)` (valida `num_preguntas` ≤ preguntas activas, rango de `porcentaje_aprobacion` 0-100)
- [ ] T081 [US4] Crear `backend/app/routers/admin.py` con endpoints de configuración: `GET /config`, `PUT /config`; aplica `require_roles(["admin"])` en ambos
- [ ] T082 [P] [US4] Crear `frontend/components/admin/ConfigForm.vue` — formulario de configuración: campos `num_preguntas` (number input, min 1), `segundos_por_pregunta` (number input, min 10), `porcentaje_aprobacion` (number input, 0-100 o null); muestra estado del sistema (configurado/no configurado); botón guardar
- [ ] T083 [US4] Crear `frontend/pages/admin/config.vue` — página de configuración (solo admin, middleware redirige editores a `/admin`): carga config actual, renderiza `ConfigForm`, muestra confirmación tras guardar; muestra advertencia si `porcentaje_aprobacion` es null

**Checkpoint**: US4 lista — administrador puede configurar el simulador sin intervención técnica

---

## Phase 7: US5 — Admin y Editor gestionan estudiantes (Prioridad: P5)

**Goal**: Admin y editor pueden crear cuentas de estudiantes directamente. Admin puede ver el historial de cualquier estudiante.

**Independent Test**: Editor `POST /api/admin/students` → nuevo estudiante puede iniciar sesión → `GET /api/admin/students/{id}` (admin) muestra historial.

### Tests para US5 ⚠️ Escribir PRIMERO

- [ ] T084 [P] [US5] Escribir test de integración `test_list_students` en `backend/tests/integration/test_admin.py` — verifica: 200 para admin y editor, paginación funcional, filtro por nombre
- [ ] T085 [P] [US5] Escribir test de integración `test_create_student_by_editor` en `backend/tests/integration/test_admin.py` — verifica: 201, nuevo usuario puede autenticarse con las credenciales creadas
- [ ] T086 [P] [US5] Escribir test de integración `test_toggle_student_status` en `backend/tests/integration/test_admin.py` — verifica: usuario desactivado recibe 403 al intentar login

### Implementación US5

- [ ] T087 [US5] Agregar métodos de gestión de estudiantes a `backend/app/services/admin_service.py`: `list_students(q, activo, page, page_size, session)`, `create_student(nombre, email, password, session)` (verifica unicidad, hashea password, rol=estudiante), `get_student_with_history(id, session)`, `toggle_student_status(id, activo, session)`
- [ ] T088 [US5] Agregar endpoints de estudiantes al router en `backend/app/routers/admin.py`: `GET /students`, `POST /students`, `GET /students/{id}`, `PATCH /students/{id}/status`; `GET /students` y `POST /students` con `require_roles(["admin", "editor"])`; `GET /students/{id}` y `PATCH /students/{id}/status` con `require_roles(["admin"])`
- [ ] T089 [P] [US5] Crear `frontend/components/admin/StudentList.vue` — tabla de estudiantes: columnas (nombre, email, estado, total intentos, último resultado); indicador visual activo/inactivo; botón "Ver detalle" (solo admin); búsqueda por nombre o email
- [ ] T090 [US5] Crear `frontend/pages/admin/students/index.vue` — listado paginado de estudiantes con `StudentList.vue`; botón "Agregar estudiante" navega a `/admin/students/new`; carga dinámica de datos con filtros
- [ ] T091 [P] [US5] Crear `frontend/pages/admin/students/new.vue` — formulario: nombre completo, email, contraseña temporal; llama `POST /api/admin/students`; redirige a `/admin/students` tras éxito con mensaje de confirmación

**Checkpoint**: US5 lista — gestión completa de estudiantes desde el panel administrativo

---

## Phase 8: US6 — Estudiante consulta historial de resultados (Prioridad: P6)

**Goal**: Estudiante puede ver todos sus intentos anteriores y revisar el detalle de cada uno.

**Independent Test**: Completar 2 exámenes → `GET /api/exams/history` retorna 2 intentos → `GET /api/exams/{id}/results` muestra detalle completo del primero.

### Tests para US6 ⚠️ Escribir PRIMERO

- [ ] T092 [P] [US6] Escribir test de integración `test_history_only_own_attempts` en `backend/tests/integration/test_exams.py` — verifica que estudiante A no puede ver intentos de estudiante B en `/api/exams/history`
- [ ] T093 [P] [US6] Escribir test de integración `test_results_not_available_during_exam` en `backend/tests/integration/test_exams.py` — verifica: 409 si se intenta `GET /api/exams/{id}/results` con intento no finalizado

### Implementación US6

- [ ] T094 [P] [US6] Crear `frontend/components/results/HistoryCard.vue` — tarjeta de intento histórico: fecha, puntuación (X/N), resultado (aprobado/reprobado en verde/rojo), botón "Ver detalle"
- [ ] T095 [US6] Crear `frontend/pages/history.vue` — historial del estudiante: lista paginada de `HistoryCard`; carga `GET /api/exams/history`; cada card enlaza a `/exam/{id}/results`
- [ ] T096 [US6] Crear `frontend/pages/admin/students/[id].vue` — detalle de estudiante para admin: info del estudiante (nombre, email, estado) + historial completo de intentos en tabla (fecha, puntuación, resultado); enlace a cada resultado

**Checkpoint**: US6 lista — historial completo accesible para estudiantes y admins

---

## Phase N: Polish y Cross-cutting Concerns

**Propósito**: Mejoras que afectan múltiples historias de usuario.

- [ ] T097 [P] Agregar manejador global de excepciones a `backend/app/main.py` — captura `RequestValidationError` (422 con mensajes legibles), `HTTPException` (pass-through), y excepciones no capturadas (500 con log)
- [ ] T098 [P] Configurar logging estructurado en `backend/app/core/settings.py` — nivel INFO en producción, DEBUG en desarrollo; formato JSON para producción
- [ ] T099 [P] Crear `nginx.conf` para producción — sirve `/static/` directamente desde volumen de imágenes, hace proxy de `/api/` al backend, hace proxy del resto al frontend Nuxt
- [ ] T100 [P] Escribir unit tests para `AuthService` en `backend/tests/unit/test_auth_service.py` — login exitoso, login con contraseña incorrecta, login con usuario inactivo
- [ ] T101 [P] Escribir unit tests para `QuestionService` en `backend/tests/unit/test_question_service.py` — import CSV con encoding correcto, soft-delete no disponible cuando intento activo
- [ ] T102 [P] Escribir tests de contrato RBAC en `backend/tests/contract/test_rbac_contracts.py` — verifica que los 3 roles solo acceden a sus endpoints permitidos (cubre todos los routers)
- [ ] T103 [P] Configurar página de error en `frontend/error.vue` — maneja 404 (página no encontrada) y 500 (error de servidor) con mensajes en español y link a inicio
- [ ] T104 [P] Agregar índices de base de datos a la migración en `backend/alembic/versions/001_initial_schema.py` — índices en `preguntas.tema`, `preguntas.activa`, `intentos_examen.estudiante_id`, `intentos_examen.finalizado_at`, `respuestas_intento.intento_id`
- [ ] T105 Ejecutar y validar todos los escenarios de `specs/001-exam-simulator/quickstart.md` contra el entorno de desarrollo; documentar y corregir cualquier discrepancia encontrada

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — puede iniciarse de inmediato
- **Foundational (Phase 2)**: Depende de la completación de Setup — BLOQUEA todas las historias
- **US1 (Phase 3)**: Depende de Foundational — es el MVP; no depende de US2, US3, US4, US5 o US6
- **US2 (Phase 4)**: Depende de Foundational; el endpoint de registro puede desarrollarse en paralelo con US1
- **US3 (Phase 5)**: Depende de Foundational; `preguntas` model ya existe desde Foundational
- **US4 (Phase 6)**: Depende de Foundational; `configuracion_examen` model ya existe desde Foundational
- **US5 (Phase 7)**: Depende de Foundational + US4 lógicamente (necesita config para que los nuevos estudiantes puedan tomar exámenes)
- **US6 (Phase 8)**: Depende de US1 (necesita intentos finalizados para mostrar historial)
- **Polish (Phase N)**: Depende de que todas las historias deseadas estén completas

### Dependencias dentro de cada historia

- Tests DEBEN escribirse y fallar ANTES de la implementación (Principio III constitución)
- Modelos → Servicios → Routers (backend)
- Composables/Stores → Componentes → Páginas (frontend)
- Backend implementado antes del frontend para cada endpoint

### Oportunidades de paralelismo

- Todas las tareas marcadas `[P]` dentro de una fase pueden ejecutarse simultáneamente
- Los tests `[P]` de una historia pueden escribirse simultáneamente entre sí
- Backend y frontend de historias diferentes pueden desarrollarse en paralelo una vez completada la Foundational

---

## Parallel Example: US1

```bash
# Escribir todos los tests de US1 juntos (TDD):
Task T034: Integration test start exam
Task T035: Integration test no config
Task T036: Integration test answer question
Task T037: Integration test get results
Task T038: Unit test fisher-yates shuffle
Task T039: Unit test score calculation

# Luego implementar backend de US1 (secuencial):
T040 → T041

# Luego frontend de US1 (paralelo donde posible):
Task T042: useTimer composable
Task T043: useExam composable
Task T044: exam store
Task T045: TimerBar component
Task T046: ProgressBar component
Task T047: AnswerOption component

# Luego:
T048 (QuestionCard — depende de AnswerOption y TimerBar)
T049 (exam page — depende de QuestionCard)
T050-T052 (results components — paralelo entre sí)
T053 (results page — depende de ScoreCard y QuestionReview)
T054 (index page — depende de useExam)
```

---

## Implementation Strategy

### MVP First (Solo US1)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO — bloquea todo)
3. Completar Phase 3: US1
4. **STOP y VALIDAR**: Ejecutar escenario 3 de quickstart.md manualmente
5. Demo: estudiante inicia examen, responde, ve resultados → MVP funcional

### Incremental Delivery

1. Setup + Foundational → Infraestructura lista
2. US1 → Examen funcional (MVP 🎯)
3. US2 → Registro autónomo de estudiantes
4. US3 → Banco de preguntas gestionable (importar CSV inicial aquí)
5. US4 → Configuración del sistema activa
6. US5 → Gestión de estudiantes desde panel
7. US6 → Historial de intentos
8. Polish → Sistema listo para producción

---

## Notes

- `[P]` = archivos distintos, sin dependencias bloqueantes entre sí
- `[USn]` = traza la tarea a la historia de usuario para visibilidad
- Tests DEBEN fallar antes de implementar (Principio III de la constitución)
- Cada historia es verificable independientemente usando su "Independent Test"
- Imágenes del banco de preguntas (`imagenes_senales/`) deben copiarse a `backend/static/` antes de ejecutar los escenarios de quickstart.md
- El seeder (T027) debe ejecutarse antes de los tests que requieran `admin_token`
