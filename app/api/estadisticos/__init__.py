from flask import Blueprint

estg_bp = Blueprint("est_graf", __name__)
from . import routes
