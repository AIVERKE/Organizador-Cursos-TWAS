from flask import render_template
from . import qrscan_bp
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required


@qrscan_bp.route("/scanning")
@login_required
@role_required(2, 4)
def scanning():
    return render_template("qrscan/scan.html")
