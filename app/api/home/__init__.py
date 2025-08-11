from flask import Blueprint

home_bp = Blueprint("home", __name__)

# Importamos las rutas después de definir el blueprint
from . import routes
