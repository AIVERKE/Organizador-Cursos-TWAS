from flask import Blueprint
notas_bp = Blueprint ("notas",__name__)
from . import routes