from flask import Blueprint

coordinador_bp = Blueprint("coordinador", __name__, template_folder="templates")

from . import routes