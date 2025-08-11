from flask import Blueprint, render_template
from app.api.coordinador import coordinador_bp
from flask_login import login_user, logout_user, login_required, current_user

@coordinador_bp.route("/")
@login_required
def index():
    return render_template("Coordinador/indexCoordinador.html")