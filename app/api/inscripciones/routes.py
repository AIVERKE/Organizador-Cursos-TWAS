from flask import Blueprint, request, jsonify, render_template
from . import ins_bp
from app.controllers import i_controller as ins
from app.controllers import c_controller as crs
from flask_login import login_required
from app.api.auth.utils import role_required


@ins_bp.route("/", methods=["GET"])
@login_required
@role_required(1,4)
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
@login_required
@role_required(1,4)
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
@login_required
@role_required(1,4)
def post_inscripcion():
    data = request.json
    ins.crear_inscripcion(
        data["id_usuario"], data["id_curso"], data["fecha_inscripcion"]
    )
    return jsonify({"mensaje": "Inscripcion creada"}), 201


@ins_bp.route("/<int:id_inscripcion>", methods=["PUT"])
@login_required
@role_required(1,4)
def put_curso(id_inscripcion):
    data = request.json
    ins.actualizar_inscripcion(
        id_inscripcion, data["id_usuario"], data["id_curso"], data["fecha_inscripcion"]
    )
    return jsonify({"mensaje": "Inscripcion actualizada"})


@ins_bp.route("/<int:id_inscripcion>", methods=["DELETE"])
@login_required
@role_required(1,4)
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

import psycopg2
from app.db_c import get_connection
from datetime import datetime,time

@ins_bp.route("/registrar_asistencia/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_curso, nombre FROM cursos;")
    cursos = [{"id": row[0], "nombre": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    # return render_template("Estudiante/Est.html", cursos=cursos)
    return render_template("Asistencia/asistencia.html", cursos=cursos)

@ins_bp.route("/registrar_asistencia/validar/", methods=["POST"])
def validar():
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "Error: no se recibieron datos",
            "message":"Error: no data received"}), 400

    correo = data.get("correo")
    curso_id = data.get("curso")
    pin = data.get("pin")

    conn = get_connection()
    cur = conn.cursor()

    # Validar correo existe
    cur.execute("SELECT id_usuario FROM usuarios WHERE email = %s;", (correo,))
    usuario = cur.fetchone()
    if not usuario:
        return jsonify({"mensaje": "Correo no registrado o incorrecto",
            "message": "Email not registered or incorrect"}), 400
    usuario_id = usuario[0]

    hoy = datetime.now()  # Ej: 2025-08-18 22:17:03

    # Validar inscripción en curso y pin
    cur.execute("""
        SELECT i.id_inscripcion,modalidad FROM inscripciones i
        WHERE i.id_usuario = %s AND i.id_curso = %s;
    """, (usuario_id, curso_id))
    inscripcion = cur.fetchone()

    if not inscripcion:
        cur.close()
        conn.close()
        return jsonify({"mensaje": "El usuario no está inscrito en este curso",
            "message": "The user is not registered in this course"}), 400
    inscripcion_id = inscripcion[0]
    modalidad = inscripcion[1]


    if modalidad == "catedra":
        # if not time(9,30) <= datetime.now().time() <= time(10,15):
        if not time.min <= datetime.now().time() <= time.max:
            return jsonify({"mensaje": "No se encuentra en horario de asistencia",
                "message": "You are out of attendance schedule"}), 400
        # Verificar si ya existe asistencia con modalidad "catedra" (solo una asistencia)
        cur.execute("""
            SELECT id_inscripcion
            FROM asistencias 
            WHERE id_inscripcion = %s AND fecha::DATE = %s
        """, (inscripcion_id, hoy.date()))

        existente = cur.fetchone()

        if existente:
            cur.close()
            conn.close()
            return jsonify({"mensaje": "Asistencia ya registrada en este curso",
                "message": "Attendance already registered in this course"}), 400
    elif modalidad == "catedra-laboratorio":
        sw_h = 0
        # if time(9,30) <= datetime.now().time() <= time(10,15):
        if time.min <= datetime.now().time() <= time(11,59,59):
            sw_h = 0
        # elif time(13,45) <= datetime.now().time() <= time(17,15):
        elif time(12,00) <= datetime.now().time() <= time.max:
            sw_h = 1
        else:
            return jsonify({"mensaje": "No se encuentra en horario de asistencia",
                "message": "You are out of attendance schedule"}), 400

        if sw_h==0:
            cur.execute("""
                SELECT id_inscripcion
                FROM asistencias 
                WHERE id_inscripcion = %s AND fecha::DATE = %s
                -- AND ((fecha::TIME BETWEEN '09:30:00' AND '10:15:00'))
                AND ((fecha::TIME BETWEEN '00:00:00' AND '11:59:59'))
            """, (inscripcion_id, hoy.date()))

            existente = cur.fetchone()

            if existente:
                cur.close()
                conn.close()
                return jsonify({"mensaje": "Asistencia ya registrada en este curso",
                    "message": "Attendance already registered in this course"}), 400
        elif sw_h==1:
            cur.execute("""
                SELECT id_inscripcion
                FROM asistencias 
                WHERE id_inscripcion = %s AND fecha::DATE = %s
                -- AND ((fecha::TIME BETWEEN '13:45:00' AND '17:15:00'))
                AND ((fecha::TIME BETWEEN '12:00:00' AND '23:59:59'))
            """, (inscripcion_id, hoy.date()))

            existente = cur.fetchone()

            if existente:
                cur.close()
                conn.close()
                return jsonify({"mensaje": "Asistencia ya registrada en este curso",
                    "message": "Attendance already registered in this course"}), 400

    ok, msg_es, msg_en ,= crs.verificar_pin(curso_id, pin, datetime.now())
    
    if ok: 
        cur.execute(
            """
            INSERT INTO asistencias (id_inscripcion, fecha, presente)
            VALUES (%s, %s, %s)
        """,
            (inscripcion[0],datetime.now(),True)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensaje": msg_es,"message": msg_en})

    cur.close()
    conn.close()
    return jsonify({"mensaje": msg_es,"message": msg_en}),400
