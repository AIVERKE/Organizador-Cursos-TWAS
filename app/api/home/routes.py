from flask import render_template
from . import home_bp



@home_bp.route("/")
def index():
    return render_template("index.html")  # O simplemente: return "Hola desde home"
