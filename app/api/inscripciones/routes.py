from flask import Blueprint, request, jsonify, render_template
from . import ins_bp
from app.controllers import i_controller as ins
from app.api.auth.utils import role_required


@ins_bp.route("/", methods=["GET"])
def get_inscripciones():
    try:
        datos = ins.obtener_inscripciones()
        inscripciones = []
        for row in datos:
            inscripciones.append(
                {
                    "id_inscripcion": row[0],
                    "id_usuario": row[1],
                    "id_curso": row[2],
                    "fecha_inscripcion": row[3],
                }
            )
        return jsonify(inscripciones)
    except Exception as e:
        print("Error al obtener inscripciones:", e)
        return (
            jsonify({"error": str(e)}),
            500,
        )  # cambié el [] que seria una coleccion vacia


@ins_bp.route("/<int:id_inscripcion>", methods=["GET"])
def get_inscripcion(id_inscripcion):
    row = ins.obtener_inscripcion(id_inscripcion)
    if row:
        inscripcion = {
            "id_inscripcion": row[0],
            "id_usuario": row[1],
            "id_curso": row[2],
            "fecha_inscripcion": row[3],
        }
        return jsonify(inscripcion)
    return jsonify({"mensaje": "Inscripcion no encontrada"}), 404


@ins_bp.route("/", methods=["POST"])
def post_inscripcion():
    data = request.json
    ins.crear_inscripcion(
        data["id_usuario"], data["id_curso"], data["fecha_inscripcion"]
    )
    return jsonify({"mensaje": "Inscripcion creada"}), 201


@ins_bp.route("/<int:id_inscripcion>", methods=["PUT"])
def put_curso(id_inscripcion):
    data = request.json
    ins.actualizar_inscripcion(
        id_inscripcion, data["id_usuario"], data["id_curso"], data["fecha_inscripcion"]
    )
    return jsonify({"mensaje": "Inscripcion actualizada"})


@ins_bp.route("/<int:id_inscripcion>", methods=["DELETE"])
def delete_inscripcion(id_inscripcion):
    ins.eliminar_inscripcion(id_inscripcion)
    return jsonify({"mensaje": "Inscripcion eliminada"})





@ins_bp.route("/usuario/<int:id_usuario>", methods=["GET"])
def get_inscripciones_por_usuario(id_usuario):
    try:
        datos = ins.obtener_inscripciones_por_usuario(id_usuario)
        resultado = []
        for row in datos:
            resultado.append({
                "id_inscripcion": row[0],
                "id_curso": row[1],
                "nombre_curso": row[2],
                "descripcion": row[3],
                "modalidad": row[4],
                "version": row[5],
                "anio": row[6]
            })
        return jsonify(resultado)
    except Exception as e:
        print("Error al obtener inscripciones por usuario:", e)
        return jsonify({"error": str(e)}), 500

