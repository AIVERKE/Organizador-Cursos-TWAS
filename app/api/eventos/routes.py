from flask import Blueprint, request, jsonify, render_template
from . import evento_bp
from app.controllers import e_controller as evt
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required

# ----- PARA COORDINADOR -----
@evento_bp.route("/coor/eventos", methods=["GET"])
@login_required
@role_required(1, 4)
def obtener_eventos_completo():
    return render_template("Coordinador/partials/eventos.html", eventos=evt.obtener_eventos_full())

@evento_bp.route('/coor/eventos/info/<int:id_evento>',methods=['GET'])
@login_required
@role_required(1, 4)
def obtener_datos_evento_json(id_evento):
    evento = evt.obtener_evento(id_evento)
    if evento:
        return jsonify(evento[0])
    return jsonify({}), 404

@evento_bp.route('/coor/version/info/<int:id_version>',methods=['GET'])
@login_required
@role_required(1, 4)
def obtener_datos_version_json(id_version):
    version = evt.obtener_eventoVs(id_version)
    if version:
        return jsonify(version[0])
    return jsonify({}), 404

@evento_bp.route("/coor/eventos/<int:id_evento>", methods=["PUT"])
@login_required
@role_required(1, 4)
def editar_evento(id_evento):
    data = request.json
    campos_requeridos = ["nombre"]
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "Datos incompletos"}), 400
    evt.actualizar_evento(id_evento,data["nombre"])

@evento_bp.route("/coor/version/<int:id_version>", methods=["PUT"])
@login_required
@role_required(1, 4)
def editar_version_evento(id_version):
    data = request.json
    campos_requeridos = ["nombre_version","anio","lugar","fecha_inicio","fecha_fin","lugar"]
    if not data or not all(k in data for k in campos_requeridos):
        return jsonify({"error": "Datos incompletos"})
    evt.actualizar_eventoVs(
        data["id_evento"],
        data["nombre_version"], 
        data["anio"], 
        data["fecha_inicio"], 
        data["fecha_fin"],
        data["lugar"],
        id_version, 
    )

@evento_bp.route("/coor/eventos", methods=["POST"])
@login_required
@role_required(1, 4)
def crear_evento():
    data = request.json
    campos = ["nombre"]
    if not data or not all(k in data for k in campos):
        return jsonify({"error": "Datos incompletos"}), 400
    evt.crear_evento(
        data["nombre"],
    )
    return jsonify({"mensaje": "Evento creado", "success": True}), 201

@evento_bp.route("/coor/version", methods=["POST"])
@login_required
@role_required(1, 4)
def crear_version_evento():
    data = request.json
    campos = ["id_evento","nombre_version","anio","fecha_inicio","fecha_fin","lugar"]
    if not data or not all(k in data for k in campos):
        return jsonify({"error": "Datos incompletos"}), 400
    evt.crear_eventoVs(
        data["id_evento"],
        data["nombre_version"],
        data["anio"],
        data["fecha_inicio"],
        data["fecha_fin"],
        data["lugar"],
    )
    return jsonify({"mensaje": "Version de evento creado"}), 201

# Ruta no utilizada
@evento_bp.route("/<int:id_evento>", methods=["GET"])
@login_required
@role_required(1, 4)
def get_evento(id_evento):
    row = evt.obtener_evento(id_evento)
    if row:
        evento = {"id_evento": row[0], "nombre_base": row[1]}
        return jsonify(evento)
    return jsonify({"mensaje": "Evento no encontrado"}), 404

# Ruta no utilizada
@evento_bp.route("/", methods=["POST"])
@login_required
@role_required(1, 4)
def post_evento():
    data = request.json
    evt.crear_evento(data["nombre_base"])
    return jsonify({"mensaje": "Evento creado"}), 201

# Ruta no utilizada
@evento_bp.route("/<int:id_evento>", methods=["PUT"])
@login_required
@role_required(1, 4)
def put_evento(id_evento):
    data = request.json
    evt.actualizar_evento(id_evento, data["nombre_base"])
    return jsonify({"mensaje": "Evento actualizado"})

# Ruta no utilizada
@evento_bp.route("/<int:id_evento>", methods=["DELETE"])
@login_required
@role_required(1, 4)
def delete_evento(id_evento):
    evt.eliminar_evento(id_evento)
    return jsonify({"mensaje": "Evento eliminado"})


# version evento

# Ruta no utilizada
@evento_bp.route("/version", methods=["GET"])
@login_required
@role_required(1, 4)
def get_eventosVs():
    try:
        datos = evt.obtener_eventosVs()
        eventosVs = []
        for row in datos:
            eventosVs.append(
                {
                    "id_version": row[0],
                    "id_evento": row[1],
                    "nombre_version": row[2],
                    "anio": row[3],
                    "fecha_inicio": row[4],
                    "fecha_fin": row[5],
                    "lugar": row[6],
                }
            )
        return jsonify(eventosVs)
    except Exception as e:
        print("Error al obtener las versiones de eventos:", e)
        return (
            jsonify({"error": str(e)}),
            500,
        )  # cambié el [] que seria una coleccion vacia

# Ruta no utilizada
@evento_bp.route("/version/<int:id_version>", methods=["GET"])
@login_required
@role_required(1, 4)
def get_eventoVs(id_version):
    row = evt.obtener_eventoVs(id_version)
    if row:
        eventoVs = {
            "id_version": row[0],
            "id_evento": row[1],
            "nombre_version": row[2],
            "anio": row[3],
            "fecha_inicio": row[4],
            "fecha_fin": row[5],
            "lugar": row[6],
        }
        return jsonify(eventoVs)
    return jsonify({"mensaje": "Version de evento no encontrado"}), 404

# Ruta no utilizada
@evento_bp.route("/version", methods=["POST"])
@login_required
@role_required(1, 4)
def post_eventoVs():
    data = request.json
    evt.crear_eventoVs(
        data["id_evento"],
        data["nombre_version"],
        data["anio"],
        data["fecha_inicio"],
        data["fecha_fin"],
        data["lugar"],
    )
    return jsonify({"mensaje": "Version de evento creado"}), 201

# Ruta no utilizada
@evento_bp.route("/version/<int:id_version>", methods=["PUT"])
@login_required
@role_required(1, 4)
def put_eventoVs(id_version):
    data = request.json
    evt.actualizar_eventoVs(
        data["id_evento"],
        data["nombre_version"],
        data["anio"],
        data["fecha_inicio"],
        data["fecha_fin"],
        data["lugar"],
        id_version,
    )

    return jsonify({"mensaje": "Version de evento actualizado"})

# Ruta no utilizada
@evento_bp.route("/version/<int:id_version>", methods=["DELETE"])
@login_required
@role_required(1, 4)
def delete_eventoVs(id_version):
    evt.eliminar_eventoVs(id_version)
    return jsonify({"mensaje": "Version de evento eliminado"})
