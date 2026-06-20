import json
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    database_url: str = "postgresql://postgres:postgres@localhost:5432/newdrivers_exams"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Admin inicial
    admin_email: str = "admin@newdrivers.com"
    admin_password: str = "Admin1234!"

    # Logging
    debug: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    if debug:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        logging.basicConfig(level=level, format=fmt)
    else:
        # Simple JSON-like format for production
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_record = {
                    "level": record.levelname,
                    "name": record.name,
                    "message": super().format(record),
                }
                return json.dumps(log_record)

        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(level=level, handlers=[handler])


settings = Settings()
