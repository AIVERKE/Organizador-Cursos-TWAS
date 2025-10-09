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
    make_response,
    flash,
)
from . import qrs_bp
from app.controllers import u_controller as est  # Importa el controlador de estudiantes
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required
from app.db_c import get_connection
from app.controllers import i_controller as ins
from datetime import datetime, timedelta, time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static/qrs"))


@qrs_bp.route("/<path:filename>", methods=["GET"])
@login_required
@role_required(3)
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
        id_curso = primera_inscripcion["id_curso"]

        horario = datetime.now().strftime("%Y-%m-%d %H:%M")

        os.makedirs(BASE_DIR, exist_ok=True)

        existing_files = [
            fname
            for fname in os.listdir(BASE_DIR)
            if fname.startswith(f"qr_{id_inscripcion}_") and fname.endswith(".png")
        ]

        if existing_files:
            return redirect(url_for("qrs.perfil_estudiante", id_usuario=id_usuario))

        contenido = (
            f"{os.getenv('URL_APP')}/qrs/registrar?"
            f"id_inscripcion={id_inscripcion}&id_curso={id_curso}"
            f"&id_usuario={id_usuario}&horario={horario}"
        )

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
@role_required(1, 2)
def registrar():
    id_inscripcion = request.args.get("id_inscripcion", type=int)
    hora_registro = datetime.now()

    if not id_inscripcion:
        return "Falta el parámetro 'id_inscripcion'", 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener horario del curso
        cursor.execute(
            """
            SELECT c.hora_inicio_asistencia, c.hora_fin_asistencia
            FROM inscripciones i
            JOIN cursos c ON i.id_curso = c.id_curso
            WHERE i.id_inscripcion = %s
            """,
            (id_inscripcion,),
        )
        horarios = cursor.fetchone()

        if horarios:
            hora_inicio, hora_fin = horarios

            if hora_inicio and hora_fin:
                fecha_hoy = hora_registro.date()
                hora_inicio_dt = datetime.combine(fecha_hoy, hora_inicio)
                hora_fin_dt = datetime.combine(fecha_hoy, hora_fin)

                if not (hora_inicio_dt <= hora_registro <= hora_fin_dt):
                    conn.close()
                    return (
                        render_template(
                            "Answers/asistencia_fuera_horario.html",
                            fecha=hora_registro,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin,
                        ),
                        400,
                    )

        # 📌 Verificar cuántas asistencias ya hay hoy
        cursor.execute(
            """
            SELECT COUNT(*) FROM asistencias
            WHERE id_inscripcion = %s AND DATE(fecha) = CURRENT_DATE
            """,
            (id_inscripcion,),
        )
        asistencias_hoy = cursor.fetchone()[0]

        if asistencias_hoy >= 2:
            conn.close()
            return (
                render_template(
                    "Answers/asistencia_registrada.html", fecha=hora_registro
                ),
                200,
            )

        # 📌 Insertar nueva asistencia
        cursor.execute(
            """
            INSERT INTO asistencias (id_inscripcion, fecha, presente)
            VALUES (%s, %s, TRUE)
            """,
            (id_inscripcion, hora_registro),
        )
        conn.commit()
        conn.close()

        return render_template("Answers/asistencia.html", fecha=hora_registro), 200

    except Exception as e:
        return f"Error al registrar la asistencia: {str(e)}", 500

@qrs_bp.route("/actualizar_horario_asistencia/<int:curso_id>", methods=["POST"])
@login_required
@role_required(1)  # Solo coordinador
def actualizar_horario_asistencia(curso_id):
    hora_inicio = request.form.get("hora_inicio")
    hora_fin = request.form.get("hora_fin")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE cursos
            SET hora_inicio_asistencia = %s, hora_fin_asistencia = %s
            WHERE id_curso = %s
            """,
            (hora_inicio, hora_fin, curso_id),
        )
        conn.commit()
        conn.close()
        flash("Horario de asistencia actualizado correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar: {e}", "danger")

    return redirect(url_for("auth.dashboard"))


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
            print("ID Inscripción👁👄👁:", id_inscripcion)
            print(row)
            qr_filename = None
            for fname in os.listdir(BASE_DIR):
                if fname.startswith(f"qr_{id_inscripcion}_") and fname.endswith(".png"):
                    qr_filename = fname
                    break

        print ("aca estoy mi king 🦍🔥🔥")
        qr_path = f"/qrs/{qr_filename}" if qr_filename else None
        print ("Ahora estoy aca estoy mi king 🦍🔥🔥🔥")
        return render_template(
            "Estudiante/Estudiante.html",
            estudiante=row,
            qr_path=qr_path,
            
        )

    except Exception as e:
        #return str(e), 500
        return "Puta madre abuela 🗣🗣🔥🔥",500

# Muestra las asistencias de un estudiante
@qrs_bp.route("/asistencias/<int:id_usuario>", methods=["GET"])
@login_required
@role_required(3)  # estudiante
def ver_asistencias(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT a.id_asistencia, a.fecha, a.presente,
                   c.nombre AS curso
            FROM asistencias a
            JOIN inscripciones i ON a.id_inscripcion = i.id_inscripcion
            JOIN cursos c ON i.id_curso = c.id_curso
            WHERE i.id_usuario = %s
            ORDER BY a.fecha DESC
            """,
            (id_usuario,),
        )

        asistencias = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("Estudiante/asistencia.html", asistencias=asistencias)

    except Exception as e:
        return f"Error al obtener asistencias: {str(e)}", 500


@qrs_bp.route("/asistencias_coordinador", methods=["GET"])
@login_required
@role_required(1)  # Coordinador
def asistencias_coordinador():
    curso_id = request.args.get("curso_id", type=int)
    print(">>> curso_id recibido:", curso_id)
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if curso_id is not None:
            cursor.execute(
                """
                SELECT a.id_asistencia,
                       u.nombre AS estudiante,
                       c.nombre AS curso,
                       a.fecha,
                       a.presente
                FROM asistencias a
                JOIN inscripciones i ON a.id_inscripcion = i.id_inscripcion
                JOIN usuarios u ON i.id_usuario = u.id_usuario
                JOIN cursos c ON i.id_curso = c.id_curso
                WHERE c.id_curso = %s
                ORDER BY u.nombre, a.fecha DESC
                """,
                (curso_id,),
            )
        else:
            cursor.execute(
                """
                SELECT a.id_asistencia,
                       u.nombre AS estudiante,
                       c.nombre AS curso,
                       a.fecha,
                       a.presente
                FROM asistencias a
                JOIN inscripciones i ON a.id_inscripcion = i.id_inscripcion
                JOIN usuarios u ON i.id_usuario = u.id_usuario
                JOIN cursos c ON i.id_curso = c.id_curso
                ORDER BY c.nombre, u.nombre, a.fecha DESC
                """
            )

        asistencias = cursor.fetchall()
        conn.close()

        return render_template(
            "Coordinador/partials/asistencias_coordinador.html",
            asistencias=asistencias,
            curso_id=curso_id,
        )

    except Exception as e:
        return f"Error al obtener asistencias: {str(e)}", 500


# -----------------PDF PARA ASISTENCIAS-----------------------
@qrs_bp.route("/asistencias_pdf/<int:curso_id>")
@login_required
@role_required(1)  # solo coordinador
def asistencias_pdf(curso_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.nombre AS estudiante,
                   c.nombre AS curso,
                   a.fecha,
                   a.presente
            FROM asistencias a
            JOIN inscripciones i ON a.id_inscripcion = i.id_inscripcion
            JOIN usuarios u ON i.id_usuario = u.id_usuario
            JOIN cursos c ON i.id_curso = c.id_curso
            WHERE c.id_curso = %s
            ORDER BY a.fecha DESC
            """,
            (curso_id,),
        )
        asistencias = cursor.fetchall()
        conn.close()

        # Creamos un buffer en memoria
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Título
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, 750, f"Reporte de Asistencias - Curso {curso_id}")

        # Encabezados de tabla
        pdf.setFont("Helvetica", 10)
        y = 720
        pdf.drawString(40, y, "N°")
        pdf.drawString(70, y, "Estudiante")
        pdf.drawString(220, y, "Fecha")
        pdf.drawString(320, y, "Hora")
        pdf.drawString(400, y, "Asistencia")

        # Datos
        y -= 20
        for i, a in enumerate(asistencias, start=1):
            fecha = a[2].strftime("%d/%m/%Y")
            hora = a[2].strftime("%H:%M")
            estado = "Presente" if a[3] else "Ausente"

            pdf.drawString(40, y, str(i))
            pdf.drawString(70, y, a[0])
            pdf.drawString(220, y, fecha)
            pdf.drawString(320, y, hora)
            pdf.drawString(400, y, estado)

            y -= 20
            if y < 50:  # salto de página
                pdf.showPage()
                y = 750

        pdf.save()

        # Preparamos el response
        buffer.seek(0)
        response = make_response(buffer.read())
        response.headers["Content-Type"] = "application/pdf"
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename=asistencias_curso_{curso_id}.pdf"

        return response

    except Exception as e:
        return f"Error al generar PDF: {str(e)}", 500
