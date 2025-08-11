from flask import Blueprint

rxls_bp = Blueprint('rxls',__name__, template_folder='templates')

from . import routes
