# New Drivers — Exam Simulator

Driving school exam simulator. Students take timed multiple-choice exams, review results with legal basis, and track their history. Admins manage questions, configuration, and student accounts.

**Stack**: FastAPI + SQLModel + Alembic · Nuxt 3 + Vue 3 + Pinia · PostgreSQL 15

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15 running (you likely have this in a container already)

### 1. Environment

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL connection. If your local container exposes Postgres on the default port:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/newdrivers_exams
```

Adjust user, password, host, and port to match your container. The backend reads this file automatically.

### 2. Create the database

Connect to your PostgreSQL instance and create the database:

```sql
CREATE DATABASE newdrivers_exams;
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
```

Run Alembic migrations (creates all tables):

```bash
alembic upgrade head
```

Seed the initial admin user:

```bash
python -m app.scripts.seed
```

Default credentials (from `.env`):
- Email: `admin@newdrivers.com`
- Password: `Admin1234!`

Start the API server:

```bash
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:3000`.

Make sure `NUXT_PUBLIC_API_BASE` in `.env` points to the running backend:

```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## Running Tests

### Backend

From the `backend/` directory:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Tests use SQLite in-memory — no database connection needed.

### Frontend

From the `frontend/` directory:

```bash
npx vitest run
```

---

## Quick Smoke Test (US1 flow)

Once both services are running:

1. Open `http://localhost:3000/login`
2. Log in as `admin@newdrivers.com` / `Admin1234!`
3. Navigate to **Configuración** and set `porcentaje_aprobacion` (e.g. 70)
4. Log out and create a student account at `/register` (or create one from the admin panel)
5. Log in as the student
6. Click **Iniciar Examen** on the dashboard
7. Answer all questions (or let the timer expire on some)
8. Review results with color-coded answers and legal basis

---

## Using Docker Compose (full stack)

If you prefer running everything in containers instead of the steps above:

```bash
# Start all services (backend + frontend + postgres)
docker compose up --build

# In a separate terminal, run migrations and seed
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed
```

Note: The `docker-compose.yml` includes its own PostgreSQL container. If you already have Postgres running on port 5432, comment out the `db` service and update `DATABASE_URL` to point to your existing container.

---

## Project Structure

```
backend/
├── app/
│   ├── core/          # settings, database, JWT, RBAC dependencies
│   ├── models/        # SQLModel: User, Pregunta, IntentoExamen, RespuestaIntento, ConfiguracionExamen
│   ├── routers/       # auth, exams (more coming: questions, admin)
│   ├── services/      # auth_service, exam_service
│   └── scripts/       # seed.py (admin user)
├── alembic/versions/  # DB migrations
└── tests/
    ├── unit/          # Service logic (SQLite in-memory)
    └── integration/   # API endpoints (SQLite in-memory)

frontend/
├── components/
│   ├── exam/          # QuestionCard, TimerBar, ProgressBar, AnswerOption
│   └── results/       # ScoreCard, QuestionReview, LegalBasisBlock
├── composables/       # useAuth, useExam, useTimer
├── stores/            # auth, exam (Pinia)
├── layouts/           # default (student), admin
├── pages/             # login, dashboard, exam/[id], exam/[id]/results, admin/
└── tests/unit/        # Vitest: TimerBar, AnswerOption, useTimer
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...@localhost:5432/newdrivers_exams` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | *(change this)* | Secret for signing JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `ADMIN_EMAIL` | `admin@newdrivers.com` | Seeded admin email |
| `ADMIN_PASSWORD` | `Admin1234!` | Seeded admin password |
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | Backend URL for the frontend |

---

## What's Implemented (MVP — US1)

- JWT authentication (access token + httpOnly refresh cookie, 3 roles: admin / editor / estudiante)
- Exam flow: start → timed questions (Fisher-Yates shuffle) → auto-finish on last answer
- Results: score, per-question color-coded review, legal basis blocks
- Student dashboard with exam history
- Admin layout shell (questions/students/config pages coming in next iterations)
- 47 automated tests (14 backend + 33 frontend)

## What's Next

See [`specs/001-exam-simulator/tasks.md`](specs/001-exam-simulator/tasks.md) for the full task list.

Next iterations: student self-registration (US2), question bank management (US3), exam configuration UI (US4), student management (US5), full history view (US6).
