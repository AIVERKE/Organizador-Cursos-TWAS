from flask import Blueprint
mail_bp = Blueprint ("mail",__name__)
from . import routes