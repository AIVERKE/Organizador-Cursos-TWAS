from flask import Blueprint, render_template
from app.api.coordinador import coordinador_bp
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required

@coordinador_bp.route("/")
@login_required
@role_required(1, 4)
def index():
    return render_template("Coordinador/indexCoordinador.html")