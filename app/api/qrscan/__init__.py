from flask import Blueprint

qrscan_bp = Blueprint("qrscan", __name__)

# Importamos las rutas después de definir el blueprint
from . import routes
