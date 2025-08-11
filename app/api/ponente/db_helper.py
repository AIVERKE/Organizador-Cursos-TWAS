import psycopg2
from app.config import DevConfig  # O la ruta correcta a tu configuración

def nueva_conexion():
    return psycopg2.connect(DevConfig.SQLALCHEMY_DATABASE_URI)
