from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.api.ponente import ponente_bp
from app.api.auth.utils import role_required
from .utils import (
    obtener_estudiantes_inscritos,
    obtener_id_curso,
    obtener_estudiantes_inscritos_nota,
    actualizar_nota_final,
    obtener_nombre_curso,
    calcular_nota_asistencia,
    actualizar_nota_acumulada,
    actualizar_nota_asistencia,
)


# ------------------- VISTAS PRINCIPALES -------------------


@ponente_bp.route("/")
@login_required
def index():
    return render_template(
        "Expositor/expositor.html",
        nombre=current_user.nombre,
        apellido=current_user.apellido,
    )


@ponente_bp.route("/datos")
@login_required
def datos():
    return render_template(
        "Expositor/datosPersonalesExp.html",
        nombre=current_user.nombre,
        apellido=current_user.apellido,
        email=current_user.email,
        documento=current_user.documento,
        pais_origen=current_user.pais_origen,
    )


@ponente_bp.route("/curso")
@login_required
def curso():
    id_curso = obtener_id_curso(current_user.id_usuario)
    if not id_curso:
        return "No se encontró un curso para este usuario", 404

    rows = obtener_estudiantes_inscritos(id_curso)
    nombre_curso, descripcion = obtener_nombre_curso(current_user.id_usuario)
    return render_template(
        "Expositor/CursoExp.html",
        estudiantes=rows,
        nombre_curso=nombre_curso,
        descripcion=descripcion,
        id_curso=id_curso,
    )


@ponente_bp.route("/calificacion")
@login_required
def calificacion():
    id_curso = obtener_id_curso(current_user.id_usuario)
    if not id_curso:
        return "No se encontró un curso para este usuario", 404

    # Calculamos la nota de asistencia automáticamente
    calcular_nota_asistencia(id_curso)

    rows = obtener_estudiantes_inscritos_nota(id_curso)
    return render_template("Expositor/calificacionExp.html", estudiantes=rows)


# ------------------- RUTAS DE NOTAS -------------------


@ponente_bp.route("/actualizar_nota", methods=["POST"])
def actualizar_nota():
    """
    Actualiza la nota acumulada o de asistencia y recalcula la nota final.
    """
    data = request.get_json()
    id_inscripcion = data.get("id_inscripcion")
    campo = data.get("campo")
    valor = data.get("valor")

    if not id_inscripcion or valor is None or not campo:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        if campo == "nota_acumulada":
            if valor > 90:
                return jsonify({"error": "La nota acumulada no puede superar 90"}), 400
            actualizar_nota_acumulada(id_inscripcion, valor)

        elif campo == "nota_asistencia":
            actualizar_nota_asistencia(id_inscripcion, valor)

        else:
            return jsonify({"error": "Campo no permitido"}), 400

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ponente_bp.route("/nota_asistencia", methods=["POST"])
def nota_asistencia():
    """
    Actualiza únicamente la nota de asistencia de un estudiante.
    """
    data = request.get_json()
    id_inscripcion = data.get("id_inscripcion")
    nota_asistencia = data.get("nota_asistencia")

    if not id_inscripcion or nota_asistencia is None:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        actualizar_nota_asistencia(id_inscripcion, nota_asistencia)
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ponente_bp.route("/nota_acumulada", methods=["POST"])
def nota_acumulada():
    """
    Actualiza únicamente la nota acumulada de un estudiante.
    """
    data = request.get_json()
    id_inscripcion = data.get("id_inscripcion")
    nota_acumulada = data.get("nota_acumulada")

    if not id_inscripcion or nota_acumulada is None:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        actualizar_nota_acumulada(id_inscripcion, nota_acumulada)
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
