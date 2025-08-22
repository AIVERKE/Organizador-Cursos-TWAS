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
                i.id_inscripcion,
                p.nombre as docente,
                p.apellido as doc_ape,
                u.nombre as nombre, 
                u.apellido as apellido, 
                u.documento as documento,
                i.modalidad as modalidad, 
                i.fecha_inscripcion as fecha_inscripcion,
                c.nombre as curso_nombre,
                n.nota_final as nota,
                cur.nombre as materia_dada
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
            LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
            WHERE u.id_rol = :rol_boton;
        """
        result = conn.execute(text(query), {"rol_boton": rol_boton})
        participants = pd.DataFrame(result.fetchall(), columns=result.keys())

    if participants.empty:
        return "No hay usuarios para este rol", 404

    for _, row in participants.iterrows():
        participante = row["nombre"] +" "+ row["apellido"]
        documento = row["documento"]
        docente = row["docente"] + " "+row["doc_ape"]
        mensaje = ''
        curso=''        
        titulo="CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025" if row["modalidad"] == 'catedra-laboratorio' and int(row["nota"]) > 64 else "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"
        if (rol_boton) == 3:
            curso = row["curso_nombre"]
            if row["modalidad"] == 'catedra-laboratorio' and int(row["nota"]) > 64 :
                mensaje=f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas\n de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
            else:
                mensaje=f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas\n de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""    
        elif (rol_boton) == 2:
            curso = row["materia_dada"] or ''
            mensaje = f"""Por su colaboración como ponente en el tema  "{curso}".\nRealizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""    
        # fecha = date.today()        
        
        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "Input", "certificate_template.jpg")
        pdf.image(template_path, 0, 0, w=842, h=595)
        
        font_path = os.path.join(base_dir, "Input", "Oi-Regular.ttf")
        pdf.add_font("Oi", "", font_path, uni=True)

        pdf.set_font("Arial", "B", 50)
        pdf.set_text_color(0, 20, 60)
        pdf.set_xy(0, 20)
        pdf.multi_cell(842, 60, titulo, 0, "C")

        pdf.set_font("Helvetica", "I", 30)
        pdf.set_text_color(60, 60, 60)
        pdf.set_xy(0, 210)
        pdf.cell(w=842, h=60, txt=participante, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(250, 250, 250)
        pdf.set_xy(150, 260)
        pdf.multi_cell(600, 15, mensaje, 0, "C")        
        if rol_boton == 3:
            pdf.set_font("Arial", "I", 14)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(0, 510)
            pdf.multi_cell(600, 14, docente+" \nDocente de Materia", 0, "C")

        file_name = f"{documento.replace(' ', '_')} {participante.replace(' ', '_')} {curso.replace(' ', '_')}"        
        pdf.output(os.path.join(folder, f"{file_name}_certificate.pdf"))

        if rol_boton == 3:
            with db.engine.begin() as conn:
                conn.execute(
                    text("UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"),
                    {"id": row["id_inscripcion"]}
                )


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

@certificate_bp.route("/descargar-certificado/<int:user_id>")
@login_required
@role_required(1, 4)
def descargar_certificado(user_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "temp_certificates")

    # Asegurarse de que la carpeta temp exista
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    # Buscar datos del usuario
    with db.engine.connect() as conn:
        query = text("""
            SELECT 
                i.id_inscripcion,
                p.nombre as docente,
                p.apellido as doc_ape,
                u.nombre as nombre, 
                u.apellido as apellido, 
                u.documento as documento,
                i.modalidad as modalidad, 
                i.fecha_inscripcion as fecha_inscripcion,
                c.nombre as curso_nombre,
                n.nota_final as nota,
                u.id_rol as rol,
                cur.nombre as materia_dada
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
            LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
            WHERE u.id_usuario = :user_id
            LIMIT 1;
        """)
        result = conn.execute(query, {"user_id": user_id}).fetchone()

    if not result:
        return "Usuario no encontrado", 404

    # Datos
    participante = result.nombre + " " + result.apellido
    documento = result.documento
    docente = 'Dr(a). '+result.docente + " " + result.doc_ape
    curso = result.curso_nombre or ''
    rol = result.rol

    # Definir título y mensaje    
    titulo = "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"    
    if rol == 3:  # Estudiante
        if result.modalidad == "catedra-laboratorio" and result.nota and int(result.nota) > 64:
            titulo = "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
            mensaje = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
        else:
            mensaje = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
    elif rol == 2:  # Expositor
        curso = result.materia_dada or ''
        mensaje = f"""Por su colaboración como ponente en el tema "{curso}". Realizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""

    # Crear PDF
    pdf = FPDF(orientation="L", unit="pt", format="A4")
    pdf.add_page()
    template_path = os.path.join(base_dir, "Input", "certificate_template.jpg")
    pdf.image(template_path, 0, 0, w=842, h=595)    

    pdf.set_font("Arial", "B", 50)
    pdf.set_text_color(0, 20, 60)
    pdf.set_xy(0, 20)
    pdf.multi_cell(842, 60, titulo, 0, "C")

    pdf.set_font("Helvetica", "I", 30)
    pdf.set_text_color(60, 60, 60)
    pdf.set_xy(0, 210)
    pdf.cell(w=842, h=60, txt=participante, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(250, 250, 250)
    pdf.set_xy(150, 260)
    pdf.multi_cell(600, 15, mensaje, 0, "C")
    if rol == 3:
        pdf.set_font("Arial", "I", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(0, 510)
        pdf.multi_cell(600, 14, docente+" \nDocente de Materia", 0, "C")
            
    file_name = f"{documento.replace(' ', '_')}_{participante.replace(' ', '_')}_{curso.replace(' ', '_')}_certificate.pdf"
    file_path = os.path.join(folder, file_name)
    pdf.output(file_path)

    # Descargar y borrar
    response = send_file(file_path, as_attachment=True, download_name=file_name)
    if rol == 3:
        with db.engine.begin() as conn:
            conn.execute(
                text("UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"),
                {"id": result.id_inscripcion}
            )
    try:
        os.remove(file_path)
        shutil.rmtree(folder)
    except Exception:
        pass

    return response


@certificate_bp.route("/enviar-certificado/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(1, 4)
def enviar_certificado(user_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "temp_certificates")

    # Leer datos del usuario junto con información necesaria para personalizar
    with db.engine.connect() as conn:
        query = text("""
            SELECT 
                i.id_inscripcion,
                p.nombre as docente,
                p.apellido as doc_ape,
                u.nombre as nombre, 
                u.apellido as apellido, 
                u.email as email,
                u.documento as documento,
                i.modalidad as modalidad, 
                i.fecha_inscripcion as fecha_inscripcion,
                c.nombre as curso_nombre,
                n.nota_final as nota,
                u.id_rol as rol,
                cur.nombre as materia_dada
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
            LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
            WHERE u.id_usuario = :user_id
            LIMIT 1;
        """)
        result = conn.execute(query, {"user_id": user_id}).fetchone()

        if not result:
            return "Usuario no encontrado", 404

        (id_inscripcion, docente, doc_ape, student, apellido, email, documento, modalidad, fecha_inscripcion, curso_nombre, nota, rol, materia_dada) = result

    if request.method == "POST":
        asunto = request.form["asunto"]
        mensaje = request.form["mensaje"]
                                                    
        # Definir título y mensaje    
        participante = student + " " + apellido
        curso = curso_nombre
        docente = 'Dr(a). '+docente + " " + doc_ape
        titulo = "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"    
        if rol == 3:  # Estudiante
            if modalidad == "catedra-laboratorio" and nota and int(nota) > 64:
                titulo = "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
                mssg = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
            else:
                mssg = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
        elif rol == 2:  # Expositor
            curso = materia_dada or ''
            mssg = f"""Por su colaboración como ponente en el tema "{curso}". Realizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""

        fecha = date.today().strftime("%Y-%m-%d")

        # Crear carpeta temporal limpia
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

        # Generar PDF
        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "Input", "certificate_template.jpg")
        pdf.image(template_path, 0, 0, w=842, h=595)

        pdf.set_font("Arial", "B", 50)
        pdf.set_text_color(0, 20, 60)
        pdf.set_xy(0, 20)
        pdf.multi_cell(842, 60, titulo, 0, "C")

        pdf.set_font("Helvetica", "I", 30)
        pdf.set_text_color(60, 60, 60)
        pdf.set_xy(0, 210)
        pdf.cell(w=842, h=60, txt=participante, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(250, 250, 250)
        pdf.set_xy(150, 260)
        pdf.multi_cell(600, 15, mssg, 0, "C")
        if rol == 3:
            pdf.set_font("Arial", "I", 14)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(0, 510)
            pdf.multi_cell(600, 14, docente+" \nDocente de Materia", 0, "C")

        file_name = f"{documento.replace(' ', '_')}_{student.replace(' ', '_')}_{apellido.replace(' ', '_')}_{curso.replace(' ', '_')}_certificate.pdf"
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

        if rol == 3:
            with db.engine.begin() as conn:
                conn.execute(
                    text("UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"),
                    {"id": id_inscripcion}
                )
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

