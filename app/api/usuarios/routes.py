from flask import Blueprint, request, jsonify, render_template
from . import usuario_bp
from app.controllers import u_controller as usu
from app.controllers import u_controller as est
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required


from app.db_c import get_connection
import psycopg2
# ----- PARA COORDINADOR -----
## ---Estudiantes
@usuario_bp.route("/coor/estudiantes", methods=["POST"])
@login_required
def crear_estudiante():
    data = request.json
    campos = ["nombre", "apellido", "email", "contrasena", "documento", "pais_origen"]
    if not data or not all(k in data for k in campos):
        return jsonify({"error": "Datos incompletos"}), 400
    usu.crear_estudiante(
        data["nombre"],
        data["apellido"],
        data["email"],
        data["contrasena"],
        data["documento"],
        data["pais_origen"],
    )
    return jsonify({"mensaje": "Estudiante creado", "success": True}), 201

@usuario_bp.route("/coor/estudiantes", methods=["GET"])
@login_required
def obtener_estudiantes():
    return render_template("Coordinador/partials/estudiantes.html", estudiantes=usu.obtener_usuarios(rol=3))

@usuario_bp.route('/coor/estudiantes/info/<int:id_u>',methods=['GET'])
def obtener_datos_estudiante_json(id_u):
    estudiante = usu.obtener_usuarios_id(3,id_u)
    if estudiante:
        return jsonify(estudiante[0])
    return jsonify({}), 404

@usuario_bp.route("/coor/estudiantes/<int:id_usuario>", methods=["PUT"])
@login_required
def editar_estudiante(id_usuario):
    data = request.json
    campos_requeridos = ["nombre", "apellido", "email", "documento", "pais_origen", "id_rol"]
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "Datos incompletos"}), 400
    contrasena = data.get("contrasena")
    usu.actualizar_estudiante(
        id_usuario,
        data["nombre"],
        data["apellido"],
        data["email"],
        contrasena,
        data["documento"],
        data["pais_origen"],
        data["id_rol"],
    )
    return jsonify({"mensaje": "Estudiante actualizado"})

@usuario_bp.route("/coor/estudiantes/<int:id_usuario>", methods=["DELETE"])
@login_required
def borrar_estudiante(id_usuario):
    try:
        usu.eliminar_estudiante(id_usuario)
        return jsonify({"mensaje": "Estudiante eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#----------------------

# Obtener materias + notas (JSON)
# @usuario_bp.route('/coor/estudiantes/info_detalle/<int:id_u>', methods=['GET'])
# @login_required
# def detalle_estudiante(id_u):
#     materias = usu.obtener_materias_estudiante(id_u)
#     disponibles = usu.obtener_cursos_disponibles(id_u)
#     return jsonify({
#         "materias": materias,
#         "disponibles": disponibles
#     })

# Obtener materias + notas (JSON)
@usuario_bp.route('/coor/estudiantes/info_detalle/<int:id_u>', methods=['GET'])
@login_required
def detalle_estudiante(id_u):
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Ambas funciones reciben el mismo cursor
        materias = usu.obtener_materias_estudiante(id_u, cursor)
        disponibles = usu.obtener_cursos_disponibles(id_u, cursor)

        return jsonify({
            "materias": materias,
            "disponibles": disponibles
        })
    except Exception as e:
        print("Error en detalle_estudiante:", e)
        return jsonify({"error": str(e)}), 500



# Añadir materia
@usuario_bp.route('/coor/estudiantes/<int:id_u>/inscripciones', methods=['POST'])
@login_required
def agregar_materia(id_u):
    data = request.json
    id_curso = data.get("id_curso")
    if not id_curso:
        return jsonify({"error": "Curso no especificado"}), 400
    usu.crear_inscripcion(id_u, id_curso)
    return jsonify({"mensaje": "Inscripción creada"}), 201

# Quitar materia
@usuario_bp.route('/coor/estudiantes/inscripciones/<int:id_insc>/<int:id_not>', methods=['DELETE'])
@login_required
def quitar_materia(id_insc,id_not):
    usu.eliminar_inscripcion(id_insc,id_not)
    return jsonify({"mensaje": "Inscripción eliminada"}), 200

#----------------------
## ---Ponentes
@usuario_bp.route("coor/expositores", methods=["GET"])
@login_required
def expositores():
    return render_template("Coordinador/partials/expositores.html",expositores=est.obtener_usuarios(2))

@usuario_bp.route("/coor/expositores", methods=["POST"])
@login_required
def crear_expositor():
    data = request.json
    campos = ["nombre", "apellido", "email", "contrasena", "documento", "pais_origen"]
    if not data or not all(k in data for k in campos):
        return jsonify({"error": "Datos incompletos"}), 400
    usu.crear_ponente(
        data["nombre"],
        data["apellido"],
        data["email"],
        data["contrasena"],
        data["documento"],
        data["pais_origen"],
    )
    return jsonify({"mensaje": "Ponente creado", "success": True}), 201

@usuario_bp.route("/coor/expositores", methods=["GET"])
@login_required
def obtener_ponente():
    return render_template("Coordinador/partials/expositores.html", expositores=usu.obtener_usuarios(rol=2))

@usuario_bp.route('/coor/expositores/info/<int:id_u>',methods=['GET'])
def obtener_datos_ponente_json(id_u):
    ponente = usu.obtener_usuarios_id(2,id_u)
    if ponente:
        return jsonify(ponente[0])
    return jsonify({}), 404

@usuario_bp.route("/coor/expositores/<int:id_usuario>", methods=["PUT"])
@login_required
def editar_ponente(id_usuario):
    data = request.json
    campos_requeridos = ["nombre", "apellido", "email", "documento", "pais_origen", "id_rol"]
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "Datos incompletos"}), 400
    contrasena = data.get("contrasena")
    usu.actualizar_ponente(
        id_usuario,
        data["nombre"],
        data["apellido"],
        data["email"],
        contrasena,
        data["documento"],
        data["pais_origen"],
        data["id_rol"],
    )
    return jsonify({"mensaje": "Ponente actualizado"})

@usuario_bp.route("/coor/expositores/<int:id_usuario>", methods=["DELETE"])
@login_required
def borrar_ponente(id_usuario):
    try:
        usu.eliminar_ponente(id_usuario)
        return jsonify({"mensaje": "Ponente eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#----------------

# Rutas para ponentes
@usuario_bp.route('/coor/expositores/<int:id_u>/dictados', methods=['GET'])
def cursos_del_ponente(id_u):
    return usu.get_cursos_ponente(id_u)

@usuario_bp.route('/coor/expositores/disponibles', methods=['GET'])
def cursos_disponibles():
    return usu.get_cursos_disponibles_para_ponente()

@usuario_bp.route('/coor/expositores/<int:id_u>/dictados', methods=['POST'])
def asignar_dictado(id_u):
    data = request.get_json()
    id_curso = data.get('id_curso')
    usu.asignar_curso_a_ponente(id_u, id_curso)
    return jsonify({"mensaje": "Curso correctamente asignado"}), 201

@usuario_bp.route('/coor/expositores/dictados/<int:id_curso>', methods=['DELETE'])
def eliminar_dictado(id_curso):
    usu.quitar_curso_a_ponente(id_curso)
    return jsonify({"mensaje": "Curso correctamente deasignado"}), 201
#----------------


# --- DEMAS ---

@usuario_bp.route("/estudiantes/<int:id_usuario>", methods=["PUT"])
@login_required
def put_estudiante(id_usuario):
    data = request.json
    est.actualizar_estudiante(
        id_usuario,
        data["nombre"],
        data["apellido"],
        data["email"],
        data["contrasena"],
        data["documento"],
        data["pais_origen"],
        data["id_rol"],
    )
    return jsonify({"mensaje": "Estudiante actualizado"})


"""@usuario_bp.route('/estudiantes', methods=['POST'])
def post_estudiante():
    data = request.json
    est.crear_estudiante(data['nombre'], data['apellido'], data['email'], data['contrasena'], data['documento'], data['pais_origen'])
    return jsonify({"mensaje": "Estudiante creado"}), 201"""


# @usuario_bp.route("/estudiantes", methods=["POST"])
# @login_required
# def post_estudiante():
#     data = request.json
#     est.crear_estudiante(
#         data["nombre"],
#         data["apellido"],
#         data["email"],
#         data["contrasena"],
#         data["documento"],
#         data["pais_origen"],
#         data["id_rol"],
#     )
#     return jsonify({"mensaje": "Estudiante creado"}), 201


"""@usuario_bp.route('/estudiantes/<int:id_usuario>', methods=['PUT'])
def put_estudiante(id_usuario):
    data = request.json
    est.actualizar_estudiante(id_usuario, data['nombre'], data['apellido'], data['email'], data['contrasena'], data['documento'], data['pais_origen'])
    return jsonify({"mensaje": "Estudiante actualizado"})
"""

@usuario_bp.route("/estudiantes/<int:id_usuario>", methods=["DELETE"])
@login_required
def delete_estudiante(id_usuario):
    est.eliminar_estudiante(id_usuario)
    return jsonify({"mensaje": "Estudiante eliminado"})



#VISTAS

@usuario_bp.route("/vista-estudiante", methods=["GET"])
@login_required
def vista_estudiante():
    from app.controllers import u_controller as est
    user_data = est.obtener_estudiante(current_user.id_usuario)
    
    return render_template(
        "Estudiante/Estudiante.html",
        estudiante=user_data
    )

