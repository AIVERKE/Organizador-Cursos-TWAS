# Importamos la librería blueprint para el programa
from flask import Blueprint

# Creamos una instancia de la clase Blueprint
qrs_bp = Blueprint("qrs", __name__, template_folder="templates")

# De este mismma directorio importamos las rutas
from . import routes
