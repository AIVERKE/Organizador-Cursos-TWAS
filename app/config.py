"""
backend/config.py
────────────────────────────────────────────────────────────────
Centraliza TODA la configuración de la aplicación.

➊  Definimos una clase BaseConfig con parámetros comunes.
➋  Creamos subclases para cada entorno: Development, Testing, Production.
➌  Flask lee la que necesites con:  app.config.from_object("backend.config.DevConfig")
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import timedelta

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV = os.getenv("FLASK_ENV", "development").lower()


def getenv(name: str, default: str | None = None) -> str:
    """Env var helper that throws if the var is missing in Production."""
    value = os.getenv(name, default)
    if value is None and ENV == "production":
        raise RuntimeError(f"Environment variable {name} is required")
    return value


# ─────────────────────────────────────────────
# Config classes
# ─────────────────────────────────────────────
class BaseConfig:
    """Parámetros comunes para todos los entornos."""

    # Seguridad
    SECRET_KEY = getenv("SECRET_KEY", "change‑me")

    # Base de datos (SQLAlchemy)
    SQLALCHEMY_DATABASE_URI = getenv(
        "DATABASE_URL",
        "postgresql://postgres:12345@localhost:5432/awesome_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    # JWT
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", SECRET_KEY)

    # Correo electrónico (Flask-Mail)
    MAIL_SERVER = getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = getenv("MAIL_USERNAME")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD")

    # Flask-Login: Remember Me
    # Duración del inicio de sesión
    REMEMBER_COOKIE_DURATION = timedelta(minutes=1)


class DevConfig(BaseConfig):
    """Configuración para desarrollo local."""

    DEBUG = True
    FLASK_ENV = "development"
    CORS_ORIGINS = ["*"]  # Permitir todo en desarrollo


class TestConfig(BaseConfig):
    """Configuración para pruebas automatizadas."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # BD en RAM para tests
    CORS_ORIGINS = ["*"]


class ProdConfig(BaseConfig):
    """Configuración para producción."""

    DEBUG = False
    FLASK_ENV = "production"

    # CORS más restrictivo
    CORS_ORIGINS = getenv("CORS_ORIGINS", "").split(",")

    # Seguridad en cookies (https)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
