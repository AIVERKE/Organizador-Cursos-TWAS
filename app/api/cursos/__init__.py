from flask import Blueprint

curso_bp = Blueprint("cursos", __name__)
from . import routes
