import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.core.security import hash_password
from app.models import User, Pregunta, ConfiguracionExamen, IntentoExamen, RespuestaIntento  # noqa: F401


TEST_DATABASE_URL = "sqlite://"  # in-memory

_ADMIN_PASSWORD = "Admin1234!"
_STUDENT_PASSWORD = "Student1234!"


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_user")
def admin_user_fixture(session):
    user = User(
        nombre_completo="Admin Test",
        email="admin@test.com",
        password_hash=hash_password(_ADMIN_PASSWORD),
        rol="admin",
        activo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="estudiante_user")
def estudiante_user_fixture(session):
    user = User(
        nombre_completo="Estudiante Test",
        email="estudiante@test.com",
        password_hash=hash_password(_STUDENT_PASSWORD),
        rol="estudiante",
        activo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="admin_token")
def admin_token_fixture(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": _ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="estudiante_token")
def estudiante_token_fixture(client, estudiante_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "estudiante@test.com", "password": _STUDENT_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
