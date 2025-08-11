import os
import segno
from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    render_template,
    redirect,
    url_for,
)
from datetime import datetime
from . import qrs_bp
from app.controllers import u_controller as est  # Importa el controlador de estudiantes
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required
from app.db_c import get_connection
from app.controllers import i_controller as ins

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static/qrs"))


@qrs_bp.route("/<path:filename>", methods=["GET"])
@login_required
def serve_qr(filename):
    return send_from_directory(BASE_DIR, filename)


@qrs_bp.route("/generate_qr/<int:id_usuario>", methods=["GET"])
@login_required
@role_required(3)
def generate_qr_by_id(id_usuario):
    try:
        row = est.obtener_estudiante(id_usuario)
        if not row:
            return "Estudiante no encontrado", 404

        datos = ins.obtener_inscripciones_usuario(id_usuario)
        if not datos:
            return "El usuario no tiene inscripciones", 404

        primera_inscripcion = datos[0]
        id_inscripcion = primera_inscripcion["id_inscripcion"]

        os.makedirs(BASE_DIR, exist_ok=True)

        # Verificar si ya existe un QR para esta inscripción
        existing_files = [
            fname
            for fname in os.listdir(BASE_DIR)
            if fname.startswith(f"qr_{id_inscripcion}_") and fname.endswith(".png")
        ]

        if existing_files:
            # Si ya existe, redirige a perfil para mostrarlo
            return redirect(url_for("qrs.perfil_estudiante", id_usuario=id_usuario))

        # Generar nuevo QR
        contenido = f"https://ca622a709762.ngrok-free.app/qrs/registrar?id_inscripcion={id_inscripcion}"
        qr = segno.make(contenido)

        filename = f"qr_{id_inscripcion}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_file = os.path.join(BASE_DIR, filename)
        qr.save(output_file, scale=10)

        return redirect(url_for("qrs.perfil_estudiante", id_usuario=id_usuario))

    except Exception as e:
        print(f"Error en generate_qr_by_id: {e}")
        return f"Error: {str(e)}", 500


@qrs_bp.route("/registrar", methods=["GET"])
@login_required
@role_required(2)
def registrar():
    id_inscripcion = request.args.get("id_inscripcion", type=int)

    if not id_inscripcion:
        return "Falta el parámetro 'id_inscripcion'", 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si ya existe una asistencia para hoy
        '''
        cursor.execute(
            """
            SELECT 1 FROM asistencias
            WHERE id_inscripcion = %s AND fecha = CURRENT_DATE
        """,
            (id_inscripcion,),
        )

        if cursor.fetchone():
            conn.close()
            return "Ya se registró asistencia para hoy.", 200
        '''
        # Insertar la asistencia
        cursor.execute(
            """
            INSERT INTO asistencias (id_inscripcion, fecha, presente)
            VALUES (%s, CURRENT_DATE, TRUE)
        """,
            (id_inscripcion,),
        )
        conn.commit()
        conn.close()

        return "Asistencia registrada correctamente.", 200

    except Exception as e:
        return f"Error al registrar la asistencia: {str(e)}", 500


# Validación de existencia de qr para Estudiante.html
@qrs_bp.route("/perfil_estudiante/<int:id_usuario>", methods=["GET"])
@login_required
@role_required(3)
def perfil_estudiante(id_usuario):
    try:
        row = est.obtener_estudiante(id_usuario)
        if not row:
            return "Estudiante no encontrado", 404

        datos = ins.obtener_inscripciones_usuario(id_usuario)
        if not datos:
            qr_filename = None
        else:
            id_inscripcion = datos[0]["id_inscripcion"]
            qr_filename = None
            for fname in os.listdir(BASE_DIR):
                if fname.startswith(f"qr_{id_inscripcion}_") and fname.endswith(".png"):
                    qr_filename = fname
                    break

        qr_path = f"/qrs/{qr_filename}" if qr_filename else None

        return render_template(
            "Estudiante/Estudiante.html",
            estudiante=row,
            qr_path=qr_path,
        )

    except Exception as e:
        return str(e), 500
