import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.settings import settings, setup_logging

setup_logging(settings.debug)

logger = logging.getLogger(__name__)


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

# Exception handlers registered before routers so the middleware stack sees them first
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
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

# Routers
from app.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
from app.routers import exams
app.include_router(exams.router, prefix="/api/exams", tags=["exams"])
from app.routers import questions as questions_router
app.include_router(questions_router.router, prefix="/api/questions", tags=["questions"])
from app.routers import admin as admin_router
app.include_router(admin_router.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "newdrivers-exams-backend"}
