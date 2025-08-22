from flask import Blueprint, request, jsonify, render_template
from . import notas_bp
from app.controllers import n_controller as notas
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required

from app.db_c import get_connection
import psycopg2


@notas_bp.route("/", methods=["GET"])
def get_notas():
    try:
        datos = notas.obtener_notas()
        notas_v = []
        for row in datos:
            notas_v.append(
                {
                    "id_nota":row[0],
                    "id_inscripcion": row[1],
                    "nota_final": row[2],
                    "nota_asistencia": row[3],
                    "nota_acumulada": row[4],
                }
            )
        return jsonify(notas_v)
    except Exception as e:
        print("Error al obtener notas:", e)
        return (
            jsonify({"error": str(e)}),
            500,
        )  # cambié el [] que seria una coleccion vacia


@notas_bp.route("/<int:id_nota>", methods=["GET"])
def get_nota(id_nota):
    row = notas.obtener_nota(id_nota)
    if row:
        nota = {
            "id_nota": row[0],
            "id_inscripcion": row[1],
            "nota_final": row[2],
            "nota_asistencia": row[3],
            "nota_acumulada": row[4],
        }
        return jsonify(nota)
    return jsonify({"mensaje": "Notas no encontradas"}), 404


@notas_bp.route("/", methods=["POST"])
def post_nota():
    data = request.json
    notas.crear_nota(
        data["id_inscripcion"], data["nota_final"], data["nota_asistencia"], data["nota_acumulada"]
    )
    return jsonify({"mensaje": "Notas creadas"}), 201


@notas_bp.route("/<int:id_nota>", methods=["PUT"])
def put_nota(id_nota):
    data = request.json
    notas.actualizar_nota(
        id_nota, data["id_inscripcion"], data["nota_final"], data["nota_asistencia"], data["nota_acumulada"]
    )
    return jsonify({"mensaje": "Notas actualizadas"})


@notas_bp.route("/<int:id_nota>", methods=["DELETE"])
def delete_nota(id_nota):
    notas.eliminar_nota(id_nota)
    return jsonify({"mensaje": "Notas eliminadas"})



