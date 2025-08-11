# Importamos la libreria blueprint para el programa
from flask import Blueprint

# Creamos una inistancia de la clase Blurprint
certificate_bp = Blueprint("certificate", __name__)

# De este mismo directorio importamos las rutas
from . import routes