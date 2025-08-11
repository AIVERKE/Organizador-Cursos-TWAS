from flask import Blueprint

ponente_bp = Blueprint("ponente", __name__, template_folder="templates")

from . import routes
from . import utils