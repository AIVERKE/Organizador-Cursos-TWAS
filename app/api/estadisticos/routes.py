from flask import Blueprint, request, jsonify, render_template
from . import estg_bp
from app.controllers import c_controller as crs
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required

# graficas

@estg_bp.route("/estadisticas/inscritos", methods=["GET"])
@login_required
@role_required(1, 4)
def inscritos_por_curso():
    try:
        ok,data = crs.generar_graf_barra()
        if ok:
            return jsonify({"success": True, "data": data})
        else: 
            return jsonify({"success": False, "error": data}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
