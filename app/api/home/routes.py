from flask import render_template
from . import home_bp
from flask_login import login_required
from app.api.auth.utils import role_required

@home_bp.route("/")
def index():
    return render_template("index.html")  # O simplemente: return "Hola desde home"
