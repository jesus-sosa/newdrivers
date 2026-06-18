# Implementation Plan: Simulador de Examen de Manejo

**Branch**: `001-exam-simulator` | **Date**: 2026-06-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-exam-simulator/spec.md`

## Summary

El módulo `newdrivers-exams` implementa un simulador de examen de licencia de manejo para la
escuela New Drivers. Los estudiantes realizan exámenes de opción múltiple (4 opciones, 1 correcta)
con temporizador individual por pregunta, retroalimentación visual inmediata y fundamento legal en
resultados. Administradores y editores gestionan el banco de preguntas (con imagen y categoría por
tema) y la configuración del simulador. La seguridad se implementa con JWT y RBAC de tres roles.

Stack: FastAPI + SQLModel + Alembic (backend) · Nuxt 3 + Vue 3 (frontend) · PostgreSQL 15+ (DB
compartida en producción, local en desarrollo).

## Technical Context

**Language/Version**: Python 3.11+ (backend) · Node.js 20+ vía Nuxt 3 (frontend)

**Primary Dependencies**:
- Backend: `fastapi`, `sqlmodel`, `alembic`, `python-jose[cryptography]`, `passlib[bcrypt]`,
  `python-multipart` (file upload), `httpx`, `pytest`, `pytest-asyncio`
- Frontend: `nuxt@3`, `vue@3`, `pinia`, `@pinia/nuxt`, `vitest`, `@nuxt/test-utils`

**Storage**: PostgreSQL 15+ — base de datos `newdrivers_exams` en la instancia compartida
gestionada por `newdrivers-infra`; en desarrollo local se levanta un contenedor PostgreSQL propio

**Testing**: pytest + httpx contra BD real en contenedor (backend); Vitest + Nuxt Test Utils
(frontend)

**Target Platform**: Servidor Linux AWS Lightsail (1 GB RAM / 2 vCPU); navegador web desktop y
móvil

**Project Type**: Aplicación web — REST API backend + SPA frontend, contenedorizada con Docker
Compose

**Performance Goals**: Resultado de examen presentado en < 3 s tras finalizar; pregunta nueva
disponible en banco en < 1 minuto

**Constraints**: 1 GB RAM en servidor compartido; JWT obligatorio en todos los endpoints
autenticados; puerto de BD no expuesto externamente; imágenes de preguntas servidas como archivos
estáticos vía Nginx

**Scale/Scope**: ~100–500 estudiantes en fase inicial; banco de preguntas ≥ 62 preguntas (muestra
provista); exámenes configurables entre 5 y 50 preguntas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Detalle |
|-----------|--------|---------|
| I. Arquitectura Multi-Repo | ✅ PASS | Este es el repo `newdrivers-exams`; un módulo = un repo |
| II. Stack Tecnológico Definido | ✅ PASS | FastAPI + SQLModel + Alembic / Nuxt 3 / PostgreSQL / Docker |
| III. Pruebas Obligatorias | ✅ PASS | pytest + httpx (backend); Vitest + Nuxt Test Utils (frontend) |
| IV. Seguridad JWT | ✅ PASS | Todos los endpoints autenticados usan JWT; RBAC a nivel de endpoint |
| V. Despliegue Containerizado | ✅ PASS | `docker-compose.yml` dev + `docker-compose.prod.yml` prod + Dockerfiles |
| VI. CI/CD CloudBuild | ✅ PASS | `cloudbuild.yaml` en raíz; deploy vía SSH a Lightsail |
| VII. Simplicidad | ✅ PASS | Sin abstracciones prematuras; YAGNI; configuración singleton |

*Post-Phase 1 re-check*: ✅ Todos los principios confirmados en el diseño de contratos y modelo
de datos. No se detectaron violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/001-exam-simulator/
├── plan.md              # Este archivo
├── research.md          # Decisiones técnicas y justificaciones
├── data-model.md        # Modelo de datos y relaciones
├── quickstart.md        # Guía de validación end-to-end
├── contracts/
│   ├── auth-api.md      # Endpoints de autenticación y registro
│   ├── questions-api.md # Endpoints del banco de preguntas
│   ├── exams-api.md     # Endpoints de sesión de examen
│   └── admin-api.md     # Endpoints de configuración y estudiantes
└── tasks.md             # Generado por /speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/           # SQLModel: User, Pregunta, ConfiguracionExamen,
│   │                     #           IntentoExamen, RespuestaIntento
│   ├── routers/          # FastAPI routers: auth, questions, exams, admin
│   ├── services/         # Business logic: auth_service, exam_service,
│   │                     #                 question_service, admin_service
│   └── core/             # settings.py, database.py, security.py (JWT),
│                         # dependencies.py (RBAC), config.py
├── alembic/              # Migraciones → base de datos newdrivers_exams
│   └── versions/
├── tests/
│   ├── unit/             # Lógica de servicios y modelos
│   ├── integration/      # Endpoints FastAPI contra BD real
│   └── contract/         # Contratos de interfaz entre módulos
└── Dockerfile

frontend/
├── components/
│   ├── exam/             # QuestionCard, TimerBar, ProgressBar, AnswerOption
│   ├── results/          # ScoreCard, QuestionReview, LegalBasisBlock
│   └── admin/            # QuestionForm, StudentList, ConfigForm, ImportForm
├── pages/
│   ├── login.vue
│   ├── register.vue
│   ├── index.vue                  # Dashboard estudiante / inicio examen
│   ├── exam/
│   │   ├── [id].vue               # Examen activo (pregunta a pregunta + timer)
│   │   └── [id]/
│   │       └── results.vue        # Resultados con retroalimentación
│   ├── history.vue                # Historial de intentos del estudiante
│   └── admin/
│       ├── index.vue              # Dashboard admin/editor
│       ├── questions/
│       │   ├── index.vue          # Listado del banco de preguntas
│       │   ├── new.vue            # Crear pregunta
│       │   └── [id]/
│       │       └── edit.vue       # Editar pregunta
│       ├── students/
│       │   ├── index.vue          # Listado de estudiantes
│       │   └── new.vue            # Crear estudiante
│       └── config.vue             # Configuración del examen (solo admin)
├── composables/
│   ├── useAuth.ts                 # Autenticación, refresh token
│   ├── useExam.ts                 # Estado del examen activo
│   └── useTimer.ts                # Countdown timer por pregunta
├── stores/
│   ├── auth.ts                    # Pinia: usuario actual, token
│   └── exam.ts                    # Pinia: intento activo, pregunta actual
├── tests/
└── Dockerfile

docker-compose.yml          # Dev: backend + frontend + postgresql local
docker-compose.prod.yml     # Prod: backend + frontend (DB en newdrivers-infra)
cloudbuild.yaml
.env.example
nginx.conf                  # Solo en producción; sirve frontend y hace proxy al backend
```

**Structure Decision**: Aplicación web (backend + frontend separados). Cada servicio tiene su
propio Dockerfile. En desarrollo, `docker-compose.yml` levanta los tres servicios. En producción,
`docker-compose.prod.yml` usa la base de datos compartida de `newdrivers-infra`.

## Complexity Tracking

> No se registran violaciones a la constitución para este módulo.
