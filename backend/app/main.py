from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nada — las migraciones se corren con alembic upgrade head
    yield
    # Shutdown


app = FastAPI(
    title="New Drivers — API del Simulador de Examen",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archivos estáticos (imágenes de señales de tránsito)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers (se agregarán conforme se implementen)
from app.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
from app.routers import exams
app.include_router(exams.router, prefix="/api/exams", tags=["exams"])
# app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
# app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "newdrivers-exams-backend"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
