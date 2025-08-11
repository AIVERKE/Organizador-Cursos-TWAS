from flask import (
    render_template,
    send_file,
    current_app,
    request,
    flash,
    redirect,
    url_for,
)
from flask_mail import Mail, Message
from sqlalchemy import text
from app import db, mail
from . import certificate_bp
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os, shutil, zipfile
from flask_login import login_user, logout_user, login_required, current_user
from app.api.auth.utils import role_required
from datetime import date

@certificate_bp.route("/generar-certificados/<int:rol_boton>")
@login_required
@role_required(1, 4)
def generar_certificados(rol_boton):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "temp_certificates")

    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    with db.engine.connect() as conn:
        query = """
            SELECT 
                u.nombre as nombre, 
                u.apellido as apellido, 
                u.documento as documento,
                i.modalidad as modalidad, 
                i.fecha_inscripcion as fecha_inscripcion,
                c.nombre as curso_nombre,
                n.nota_final as nota
            FROM usuarios u
            JOIN inscripciones i ON i.id_usuario = u.id_usuario
            JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            WHERE u.id_rol = :rol_boton
            AND (n.nota_final > 51 OR n.nota_final IS NULL);
        """
        result = conn.execute(text(query), {"rol_boton": rol_boton})
        participants = pd.DataFrame(result.fetchall(), columns=result.keys())

    if participants.empty:
        return "No hay usuarios para este rol", 404

    for _, row in participants.iterrows():
        participante = row["nombre"] +" "+ row["apellido"]
        documento = row["documento"]
        curso=''
        if (rol_boton) == 3:
            curso = row["curso_nombre"] + " " +"aprobado" if row["modalidad"] == 'catedra-laboratorio' and int(row["nota"]) > 51 else "participado"
        elif (rol_boton) == 2:
            curso = row["curso_nombre"]+' (Expositor)'    
        fecha = date.today()        
        
        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "input", "certificate_template.jpg")
        pdf.image(template_path, 0, 0, w=842, h=595)

        pdf.set_font("Helvetica", "B", 50)
        pdf.set_text_color(139, 119, 40)
        pdf.set_xy(0, 230)
        pdf.cell(w=842, h=60, txt=participante, align="C")

        pdf.set_font("Helvetica", "", 25)
        pdf.set_xy(0, 360)
        pdf.cell(w=842, h=30, txt=curso, align="C")

        pdf.set_font("Helvetica", "I", 16)
        pdf.set_text_color(1, 1, 1)
        pdf.set_xy(155, 500)
        pdf.cell(w=842, h=20, txt=str(fecha), align="C")

        file_name = f"{documento.replace(' ', '_')} {participante.replace(' ', '_')} {curso.replace(' ', '_')}"        
        pdf.output(os.path.join(folder, f"{file_name}_certificate.pdf"))

    zip_name = f"certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    if rol_boton == 3:
        zip_name = f"ESTUDIANTES: certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    elif rol_boton == 2:     
        zip_name = f"EXPOSITORES: certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(base_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                zipf.write(os.path.join(folder, file), arcname=file)

    return send_file(zip_path, as_attachment=True)


from datetime import date

@certificate_bp.route("/enviar-certificado/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(1, 4)
def enviar_certificado(user_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "temp_certificates")

    # Leer datos del usuario junto con información necesaria para personalizar
    with db.engine.connect() as conn:
        query = text("""
            SELECT u.nombre, u.apellido, u.email, u.documento, u.id_rol,
                   i.modalidad, i.fecha_inscripcion, c.nombre AS curso_nombre,
                   n.nota_final AS nota
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            WHERE u.id_usuario = :user_id
            LIMIT 1
        """)
        result = conn.execute(query, {"user_id": user_id}).fetchone()

        if not result:
            return "Usuario no encontrado", 404

        (student, apellido, email, documento, rol,
         modalidad, fecha_inscripcion, curso_nombre, nota) = result

    if request.method == "POST":
        asunto = request.form["asunto"]
        mensaje = request.form["mensaje"]

        # Preparar texto del curso según rol
        curso_texto = ""
        if rol == 3:
            aprobado = (modalidad == 'catedra-laboratorio' and nota and nota > 51)
            curso_texto = f"{curso_nombre} {'aprobado' if aprobado else 'participado'}"
        elif rol == 2:
            curso_texto = f"{curso_nombre} (Expositor)"
        else:
            curso_texto = curso_nombre or ""

        fecha = date.today().strftime("%Y-%m-%d")

        # Crear carpeta temporal limpia
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

        # Generar PDF
        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "input", "certificate_template.jpg")
        pdf.image(template_path, 0, 0, w=842, h=595)

        pdf.set_font("Helvetica", "B", 50)
        pdf.set_text_color(139, 119, 40)
        pdf.set_xy(0, 230)
        pdf.cell(w=842, h=60, txt=f"{student} {apellido}", align="C")

        pdf.set_font("Helvetica", "", 25)
        pdf.set_xy(0, 360)
        pdf.cell(w=842, h=30, txt=curso_texto, align="C")

        pdf.set_font("Helvetica", "I", 16)
        pdf.set_text_color(1, 1, 1)
        pdf.set_xy(155, 500)
        pdf.cell(w=842, h=20, txt=fecha, align="C")

        file_name = f"{documento.replace(' ', '_')}_{student.replace(' ', '_')}_{apellido.replace(' ', '_')}_{curso_texto.replace(' ', '_')}_certificate.pdf"
        output_path = os.path.join(folder, file_name)
        pdf.output(output_path)

        # Enviar correo con manejo de error
        msg = Message(subject=asunto, sender=os.getenv("MAIL_USERNAME"), recipients=[email])
        msg.body = mensaje
        try:
            with open(output_path, "rb") as f:
                msg.attach(filename=file_name, content_type="application/pdf", data=f.read())
            mail.send(msg)
            flash(f"Certificado enviado a {email}", "success")
        except Exception as e:
            flash(f"Error al enviar certificado a {email}: {str(e)}", "error")

        # Limpiar carpeta temporal
        shutil.rmtree(folder)

        return redirect(url_for("certificate.enviar_certificado", user_id=user_id))

    # GET - Mostrar formulario
    return render_template(
        "Certificados/SendCertificadoUnico.html",
        student=student,
        apellido=apellido,
        email=email,
    )


@certificate_bp.route("/enviar-certificados-todos/<int:rol_boton>", methods=["GET", "POST"])
@login_required
@role_required(1, 4)
def enviar_certificados_todos(rol_boton):
    if request.method == "POST":
        asunto = request.form.get("asunto")
        mensaje = request.form.get("mensaje")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, "temp_certificates")
        os.makedirs(folder, exist_ok=True)

        with db.engine.connect() as conn:
            query = text("""
                SELECT 
                    u.id_usuario,
                    u.nombre,
                    u.apellido,
                    u.documento,
                    u.email,
                    i.modalidad,
                    i.fecha_inscripcion,
                    c.nombre as curso_nombre,
                    n.nota_final as nota
                FROM usuarios u
                JOIN inscripciones i ON i.id_usuario = u.id_usuario
                JOIN cursos c ON c.id_curso = i.id_curso
                LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
                WHERE u.id_rol = :rol_boton
                AND (n.nota_final > 51 OR n.nota_final IS NULL);
            """)
            usuarios = conn.execute(query, {"rol_boton": rol_boton}).fetchall()

        if not usuarios:
            flash("No hay usuarios para este rol.", "warning")
            return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

        errores_envio = []
        exitos_envio = []

        for user in usuarios:
            user_id, nombre, apellido, documento, email, modalidad, fecha_inscripcion, curso_nombre, nota = user

            participante = f"{nombre} {apellido}"

            curso = ''
            if rol_boton == 3:
                # Para estudiantes: 'aprobado' o 'participado'
                if modalidad == 'catedra-laboratorio' and (nota is not None and int(nota) > 51):
                    curso = f"{curso_nombre} aprobado"
                else:
                    curso = f"{curso_nombre} participado"
            elif rol_boton == 2:
                # Para expositores
                curso = f"{curso_nombre} (Expositor)"
            else:
                curso = curso_nombre or ''

            fecha = datetime.today().strftime("%Y-%m-%d")

            # Crear PDF
            pdf = FPDF(orientation="L", unit="pt", format="A4")
            pdf.add_page()
            template_path = os.path.join(base_dir, "input", "certificate_template.jpg")
            pdf.image(template_path, 0, 0, w=842, h=595)

            pdf.set_font("Helvetica", "B", 50)
            pdf.set_text_color(139, 119, 40)
            pdf.set_xy(0, 230)
            pdf.cell(w=842, h=60, txt=participante, align="C")

            pdf.set_font("Helvetica", "", 25)
            pdf.set_xy(0, 360)
            pdf.cell(w=842, h=30, txt=curso, align="C")

            pdf.set_font("Helvetica", "I", 16)
            pdf.set_text_color(1, 1, 1)
            pdf.set_xy(155, 500)
            pdf.cell(w=842, h=20, txt=fecha, align="C")

            file_name = f"{documento.replace(' ', '_')}_{participante.replace(' ', '_')}_{curso.replace(' ', '_')}.pdf"
            output_path = os.path.join(folder, file_name)
            pdf.output(output_path)

            # Enviar correo
            msg = Message(subject=asunto, sender=os.getenv("MAIL_USERNAME"), recipients=[email])
            msg.body = mensaje

            try:
                with open(output_path, "rb") as f:
                    msg.attach(filename=file_name, content_type="application/pdf", data=f.read())
                mail.send(msg)
                exitos_envio.append(email)
            except Exception as e:
                errores_envio.append((email, str(e)))

        shutil.rmtree(folder)

        flash(f"Certificados enviados a {len(exitos_envio)} usuarios.", "success")
        if errores_envio:
            flash(f"Errores al enviar a: {', '.join(e[0] for e in errores_envio)}", "error")

        return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

    # GET: mostrar formulario
    return render_template("Certificados/SendMuchosCertificados.html", rol_boton=rol_boton)

