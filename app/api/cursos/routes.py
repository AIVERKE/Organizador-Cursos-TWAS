from flask import Blueprint, request, jsonify, render_template
from . import curso_bp
from app.controllers import c_controller as crs
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required


@curso_bp.route("/coor/cursos", methods=["GET"])
@login_required
@role_required(1, 4)
def cursos():
    return render_template(
        "Coordinador/partials/cursos.html", cursos=crs.obtener_cursos_full()
    )


@curso_bp.route("/coor/cursos/info/<int:id_curso>", methods=["GET"])
@login_required
@role_required(1, 4)
def cursos_id(id_curso):
    curso = crs.obtener_curso_id(id_curso)
    if curso:
        return jsonify(curso[0])
    return jsonify({}), 404


@curso_bp.route("/coor/cursos/<int:id_curso>", methods=["PUT"])
@login_required
@role_required(1, 4)
def actualizar_curso_base(id_curso):
    data = request.json
    campos_requeridos = ["nombre", "descripcion", "modalidad"]
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "Datos incompletos"}), 400
    crs.actualizar_curso_base(
        id_curso,
        data["nombre"],
        data["descripcion"],
        data["modalidad"],
    )
    return jsonify({"mensaje": "Curso actualizado"})


@curso_bp.route("/coor/cursos", methods=["POST"])
@login_required
@role_required(1, 4)
def crear_curso():
    data = request.json
    crs.crear_curso(
        data["nombre"],
        data["descripcion"],
        data["modalidad"],
        data["id_version"],
        data["id_ponente"],
    )
    return jsonify({"mensaje": "Curso creado"}), 201


@curso_bp.route("/coor/cursos/<int:id_curso>", methods=["DELETE"])
@login_required
@role_required(1, 4)
def eliminar_curso(id_curso):
    try:
        crs.eliminar_curso(id_curso)
        return jsonify({"mensaje": "Curso eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Ruta no utilizada
@curso_bp.route("/<int:id_curso>", methods=["GET"])
@login_required
@role_required(1, 4)
def get_curso(id_curso):
    row = crs.obtener_curso(id_curso)
    if row:
        curso = {
            "id_curso": row[0],
            "nombre": row[1],
            "descripcion": row[2],
            "modalidad": row[3],
            "id_version": row[4],
            "id_ponente": row[5],
        }
        return jsonify(curso)
    return jsonify({"mensaje": "Curso no encontrado"}), 404

# RUta no utilizada
@curso_bp.route("/", methods=["POST"])
@login_required
@role_required(1, 4)
def post_curso():
    data = request.json
    crs.crear_curso(
        data["nombre"],
        data["descripcion"],
        data["modalidad"],
        data["id_version"],
        data["id_ponente"],
    )
    return jsonify({"mensaje": "Curso creado"}), 201

# RUta no utilizada
@curso_bp.route("/<int:id_curso>", methods=["PUT"])
@login_required
@role_required(1, 4)
def put_curso(id_curso):
    data = request.json
    crs.actualizar_curso(
        id_curso,
        data["nombre"],
        data["descripcion"],
        data["modalidad"],
        data["id_version"],
        data["id_ponente"],
    )
    return jsonify({"mensaje": "Curso actualizado"})

# Ruta no utilizada
@curso_bp.route("/<int:id_curso>", methods=["DELETE"])
@login_required
@role_required(1, 4)
def delete_curso(id_curso):
    crs.eliminar_curso(id_curso)
    return jsonify({"mensaje": "Curso eliminado"})

@curso_bp.route("/coor/cursos/<int:id_curso>/ponente", methods=["GET"])
@login_required
@role_required(1, 4)
def obtener_ponente_curso(id_curso):
    ponente = crs.obtener_ponente_de_curso(id_curso)
    return jsonify(ponente)

@curso_bp.route("/coor/cursos/ponentes-disponibles", methods=["GET"])
@login_required
@role_required(1, 4)
def obtener_ponentes_disponibles():
    disponibles = crs.obtener_ponentes_disponibles()
    return jsonify(disponibles)


@curso_bp.route("/coor/cursos/<int:id_curso>/asignar_ponente", methods=["POST"])
@login_required
@role_required(1, 4)
def asignar_ponente(id_curso):
    id_ponente = request.json.get("id_ponente")
    crs.asignar_ponente(id_curso, id_ponente)
    return jsonify({"mensaje": "Ponente asignado"})


@curso_bp.route("/coor/cursos/<int:id_curso>/desasignar_ponente", methods=["DELETE"])
@login_required
@role_required(1, 4)
def desasignar_ponente(id_curso):
    crs.asignar_ponente(id_curso, 1)  # 1 = sin ponente
    return jsonify({"mensaje": "Ponente desasignado"})


# ---------- PIN:

@curso_bp.route("/pin/<int:id_curso>/nuevo_pin", methods=["POST"])
@login_required
@role_required(1, 4)
def actualizar_pin(id_curso):
    try:
        nuevo_pin, exp = crs.actualizar_pin_curso(id_curso)
        if nuevo_pin:
            return jsonify({"success": True, "nuevo_pin": nuevo_pin, "expiracion": exp})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Verificar PIN ingresado
@curso_bp.route("/pin/<int:id_curso>/verificar_pin", methods=["POST"])
@login_required
def verificar_pin(id_curso):
    try:
        data = request.get_json()
        pin = data.get("pin")
        ok, msg = crs.verificar_pin(id_curso, pin)
        if ok:
            return jsonify({"success": True, "mensaje": msg})
        else:
            return jsonify({"success": False, "mensaje": msg})
    except Exception as e:
        return jsonify({"success": False, "mensaje": "Error al Verificar"}), 400


# ---------- NUEVA RUTA: participantes (docente + estudiantes)
@curso_bp.route("/coor/cursos/<int:id_curso>/participantes", methods=["GET"])
@login_required
@role_required(1, 4)
def obtener_participantes_curso(id_curso):
    try:
        curso_info = crs.obtener_estudiantes_y_docente(id_curso)
        if curso_info:
            return jsonify(curso_info)
        return jsonify({"mensaje": "Curso no encontrado o sin estudiantes"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500