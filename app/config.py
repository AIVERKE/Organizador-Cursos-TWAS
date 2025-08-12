from __future__ import annotations
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# Carga el .env automáticamente (debe estar en la raíz del proyecto o en el mismo lugar que config.py)
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV = os.getenv("FLASK_ENV", "development").lower()


def getenv(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None and ENV == "production":
        raise RuntimeError(f"Environment variable {name} is required in production")
    return value


class BaseConfig:
    SECRET_KEY = getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    MAIL_SERVER = getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = getenv("MAIL_USERNAME")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD")

    CORS_ORIGINS = getenv("CORS_ORIGINS", "*").split(",")
    REMEMBER_COOKIE_DURATION = timedelta(
        minutes=int(getenv("REMEMBER_COOKIE_DURATION", "30"))
    )


class DevConfig(BaseConfig):
    DEBUG = True
    FLASK_ENV = "development"


class ProdConfig(BaseConfig):
    DEBUG = False
    FLASK_ENV = "production"
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


# Selección automática de configuración según ENV
config_by_name = {
    "development": DevConfig,
    "production": ProdConfig,
}

Config = config_by_name.get(ENV, DevConfig)
