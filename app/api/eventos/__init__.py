from flask import Blueprint
evento_bp = Blueprint ("eventos",__name__)
from . import routes