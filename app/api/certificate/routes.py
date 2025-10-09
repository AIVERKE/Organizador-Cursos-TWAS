from flask import (
    render_template,
    send_file,
    current_app,
    request,
    flash,
    redirect,
    url_for,
)
import io
import segno
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
from . import utils
import unicodedata

# Módulos necesarios para el nuevo enfoque de smtplib
from email.message import EmailMessage
import smtplib
import mimetypes


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
                u.id_usuario,
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
                cur.nombre as materia_dada,
                cur.id_curso as id_curso_doc
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
        participante = f"{row['nombre'] or ''} {row['apellido'] or ''}".strip()
        documento = row["documento"] or "CERT"
        docente = f"{row['docente'] or ''} {row['doc_ape'] or ''}".strip()
        mensaje = ""
        curso = ""
        titulo = (
            "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
            if row["modalidad"] == "catedra-laboratorio" and int(row["nota"]) > 64
            else "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"
        )
        if (rol_boton) == 3:
            curso = row["curso_nombre"] or ""
            if row["modalidad"] == "catedra-laboratorio" and int(row["nota"]) > 64:
                mensaje = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas\n de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
            else:
                mensaje = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas\n de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
        elif (rol_boton) == 2:
            curso = row["materia_dada"] or ""
            mensaje = f"""Por su colaboración como ponente en el tema  "{curso}".\nRealizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""
        # fecha = date.today()

        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "Input", "certificate_template.jpg")
        pdf.image(template_path, 0, 0, w=842, h=595)

        if rol_boton == 3:
            # 1. Generar QR con la URL de validación
            url = f"{os.getenv('URL_APP')}/cert/verificar/{row['id_inscripcion']}-0"
            qr_img = segno.make(url)

            # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
            qr_path = os.path.join(folder, f"qr_{row['id_inscripcion']}.png")
            qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

            # 3. Insertar QR en el PDF
            pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño
        elif rol_boton == 2:
            url = f"{os.getenv('URL_APP')}/cert/verificar/{row['id_usuario'] or ''}-{row['id_curso_doc']}"
            qr_img = segno.make(url)

            # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
            qr_path = os.path.join(
                folder, f"qr_{row['id_usuario'] or ''}-{row['id_curso_doc']}.png"
            )
            qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

            # 3. Insertar QR en el PDF
            pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño

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
            pdf.multi_cell(600, 14, docente + " \nDocente de Materia", 0, "C")

        file_name = f"{documento.replace(' ', '_')} {participante.replace(' ', '_')} {curso.replace(' ', '_')}"
        file_name = utils.sanitize_filename(file_name)
        pdf.output(os.path.join(folder, f"{file_name}_certificate.pdf"))

        if rol_boton == 3:
            with db.engine.begin() as conn:
                conn.execute(
                    text(
                        "UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"
                    ),
                    {"id": row["id_inscripcion"]},
                )

    zip_name = f"certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    if rol_boton == 3:
        zip_name = (
            f"ESTUDIANTES: certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    elif rol_boton == 2:
        zip_name = (
            f"EXPOSITORES: certificados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    zip_path = os.path.join(base_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                zipf.write(os.path.join(folder, file), arcname=file)

    return send_file(zip_path, as_attachment=True)


@certificate_bp.route("/descargar-certificado/<int:user_id>")
@login_required
@role_required(1, 2, 3, 4)
def descargar_certificado(user_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "temp_certificates")

    # Asegurarse de que la carpeta temp exista
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    # Buscar datos del usuario
    with db.engine.connect() as conn:
        query = text(
            """
            SELECT 
                u.id_usuario,
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
                cur.nombre as materia_dada,
                cur.id_curso as id_curso_doc
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
            LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
            WHERE u.id_usuario = :user_id
            LIMIT 1;
        """
        )
        result = conn.execute(query, {"user_id": user_id}).fetchone()

    if not result:
        return "Usuario no encontrado", 404

    # Datos
    participante = result.nombre + " " + result.apellido
    documento = result.documento or "CERT"
    docente = f"Dr(a). {result.docente or ''} {result.doc_ape or ''}".strip()
    curso = result.curso_nombre or ""
    rol = result.rol

    # Definir título y mensaje
    titulo = "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"
    if rol == 3:  # Estudiante
        if (
            result.modalidad == "catedra-laboratorio"
            and result.nota
            and int(result.nota) > 64
        ):
            titulo = (
                "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
            )
            mensaje = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
        else:
            mensaje = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
    elif rol == 2:  # Expositor
        curso = result.materia_dada or ""
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
        pdf.multi_cell(600, 14, docente + " \nDocente de Materia", 0, "C")

        # 1. Generar QR con la URL de validación
        url = f"{os.getenv('URL_APP')}/cert/verificar/{result.id_inscripcion}-0"
        qr_img = segno.make(url)

        # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
        qr_path = os.path.join(folder, f"qr_{result.id_inscripcion}.png")
        qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

        # 3. Insertar QR en el PDF
        pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño

    elif rol == 2:
        url = f"{os.getenv('URL_APP')}/cert/verificar/{result.id_usuario or ''}-{result.id_curso_doc}"
        qr_img = segno.make(url)

        # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
        qr_path = os.path.join(
            folder, f"qr_{result.id_usuario or ''}-{result.id_curso_doc}.png"
        )
        qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

        # 3. Insertar QR en el PDF
        pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño

    file_name = f"{documento.replace(' ', '_')}_{participante.replace(' ', '_')}_{curso.replace(' ', '_')}_certificate.pdf"
    file_path = os.path.join(folder, file_name)
    pdf.output(file_path)

    # Descargar y borrar
    response = send_file(file_path, as_attachment=True, download_name=file_name)
    if rol == 3:
        with db.engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"
                ),
                {"id": result.id_inscripcion},
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
    print(f'base_dir_debug {base_dir}')
    print(f'debug:folder {folder}')
    # Leer datos del usuario junto con información necesaria para personalizar
    with db.engine.connect() as conn:
        query = text(
            """
            SELECT 
                u.id_usuario,
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
                cur.nombre as materia_dada,
                cur.id_curso as id_curso_doc
            FROM usuarios u
            LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
            LEFT JOIN cursos c ON c.id_curso = i.id_curso
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
            LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
            WHERE u.id_usuario = :user_id
            LIMIT 1;
        """
        )
        result = conn.execute(query, {"user_id": user_id}).fetchone()

        if not result:
            return "Usuario no encontrado", 404

        (
            id_usuario,
            id_inscripcion,
            docente,
            doc_ape,
            student,
            apellido,
            email,
            documento,
            modalidad,
            fecha_inscripcion,
            curso_nombre,
            nota,
            rol,
            materia_dada,
            id_curso_doc,
        ) = result
        docente = docente or ''
        docente = docente.replace('\xa0', ' ').strip()
        doc_ape = doc_ape or ''
        doc_ape = doc_ape.replace('\xa0', ' ').strip()
        student = student.replace('\xa0', ' ').strip()
        apellido = apellido.replace('\xa0', ' ').strip()
        documento = documento or ''
        documento = documento.replace('\xa0', ' ').strip()
        curso_nombre = curso_nombre or ''
        curso_nombre = curso_nombre.replace('\xa0', ' ').strip()
        # materia_dada puede ser None, por eso se maneja diferente
        materia_dada = materia_dada.replace('\xa0', ' ').strip() if materia_dada else None
        email = email.replace('\xa0', '').strip()

    if request.method == "POST":
        asunto_sucio = request.form["asunto"]
        mensaje_sucio = request.form["mensaje"]

        # Limpieza estricta de \xa0 y saltos de línea/espacios externos
        asunto = asunto_sucio.replace('\xa0', ' ').strip()
        mensaje = mensaje_sucio.replace('\xa0', ' ').strip()

        # Definir título y mensaje
        participante = student + " " + apellido
        curso = curso_nombre
        docente = "Dr(a). " + docente + " " + doc_ape
        titulo = "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"
        if rol == 3:  # Estudiante
            if modalidad == "catedra-laboratorio" and nota and int(nota) > 64:
                titulo = "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
                mssg = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
            else:
                mssg = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
        elif rol == 2:  # Expositor
            curso = materia_dada or ""
            mssg = f"""Por su colaboración como ponente en el tema "{curso}". Realizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""

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
            pdf.multi_cell(600, 14, docente + " \nDocente de Materia", 0, "C")

            # 1. Generar QR con la URL de validación
            url = f"{os.getenv('URL_APP')}/cert/verificar/{id_inscripcion}-0"
            qr_img = segno.make(url)

            # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
            qr_path = os.path.join(folder, f"qr_{id_inscripcion}.png")
            qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

            # 3. Insertar QR en el PDF
            pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño

        elif rol == 2:
            url = f"{os.getenv('URL_APP')}/cert/verificar/{id_usuario or ''}-{id_curso_doc}"
            qr_img = segno.make(url)

            # 2. Guardar QR en archivo temporal (FPDF no acepta BytesIO directamente)
            qr_path = os.path.join(folder, f"qr_{id_usuario or ''}-{id_curso_doc}.png")
            qr_img.save(qr_path, scale=5)  # scale=5 controla el tamaño

            # 3. Insertar QR en el PDF
            pdf.image(qr_path, x=740, y=500, w=80, h=80)  # ajusta x,y,w,h a tu diseño
        
        file_name = f"{documento.replace(' ', '_')}_{student.replace(' ', '_')}_{apellido.replace(' ', '_')}_{curso.replace(' ', '_')}_certificate.pdf"        
        file_name = utils.sanitize_filename(file_name)
        
        output_path = os.path.join(folder, file_name)
        pdf.output(output_path)        
    
        mail_address = os.getenv("MAIL_USERNAME").replace('\xa0', '').strip()
        safe_sender_name = "TYAN" # o "TYAN FCPN"
        final_sender = f"{safe_sender_name} <{mail_address}>"
        asunto = "Holaaaa"
        mensaje = "Holaaaa"
        msg = Message(
            subject=asunto, 
            sender=final_sender, 
            recipients=[email.replace('\xa0','').strip()],
            charset="utf-8"
        )        
        
        msg.body = mensaje.encode('ascii', 'ignore').decode('ascii') # Limpieza ASCII agresiva
        # Aplicar la limpieza más estricta a la variable del cuerpo:
        clean_body = mensaje.replace('\xa0', ' ').strip() 
        msg.body = clean_body.encode('ascii', 'ignore').decode('ascii') # Limpieza ASCII estricta
        try:            
        
            # 1. Definir credenciales y remitente seguro (como en la otra función)
            mail_address = os.getenv("MAIL_USERNAME").replace('\xa0', '').strip()
            app_password = os.getenv("MAIL_PASSWORD") 
            final_filename = file_name.replace('\xa0', ' ').strip()
            
            # 2. Crear el objeto EmailMessage
            msg = EmailMessage()
            msg["From"] = f"TYAN <{mail_address}>" # Remitente forzado, puramente ASCII. ¡Clave para solucionar el \xa0!
            msg["To"] = email.replace('\xa0', '').strip()
            msg["Subject"] = "Certificado de Participación/Aprobación" # Usar un asunto limpio, o tu variable 'asunto' limpia.
            
            # 3. Definir el cuerpo del mensaje (limpio)
            mensaje_limpio = mensaje.replace('\xa0', ' ').strip()
            msg.set_content(mensaje_limpio)
            
            # 4. Adjuntar el PDF generado
            with open(output_path, "rb") as f:
                # Guess type (opcional, pero buena práctica)
                mime_type = mimetypes.guess_type(final_filename)[0] or 'application/pdf'
                maintype, subtype = mime_type.split('/', 1)
                
                msg.add_attachment(f.read(), 
                                  maintype=maintype, 
                                  subtype=subtype, 
                                  filename=final_filename)
                                  
            # 5. Enviar usando SMTPLIB (Conexión segura SSL)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(mail_address, app_password)
                smtp.send_message(msg)   
            
            flash(f"Certificado enviado a {email}", "success")
            if rol == 3:
                with db.engine.begin() as conn:
                    conn.execute(
                        text(
                            "UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"
                        ),
                        {"id": id_inscripcion},
                    )
        except Exception as e:
            print(">>> FINAL FILENAME:", repr(final_filename))
            print(file_name)
            print(mensaje)
            print(asunto)
            print(e)
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
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

        with db.engine.connect() as conn:
            query = text(
                """
                SELECT 
                    u.id_usuario,
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
                    cur.nombre as materia_dada,
                    cur.id_curso as id_curso_doc
                FROM usuarios u
                LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
                LEFT JOIN cursos c ON c.id_curso = i.id_curso
                LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
                LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
                LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
                WHERE u.id_rol = :rol_boton;
            """
            )
            usuarios = conn.execute(query, {"rol_boton": rol_boton}).fetchall()

        if not usuarios:
            flash("No hay usuarios para este rol.", "warning")
            return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

        errores_envio, exitos_envio = [], []

        # Configuración de correo (Tomado de la función de referencia)
        mail_address = os.getenv("MAIL_USERNAME").replace('\xa0', '').strip()
        app_password = os.getenv("MAIL_PASSWORD")
        safe_sender_name = "TYAN"

        for user in usuarios:
            (
                id_usuario,
                id_inscripcion,
                docente,
                doc_ape,
                nombre,
                apellido,
                email,
                documento,
                modalidad,
                fecha_inscripcion,
                curso_nombre,
                nota,
                rol,
                materia_dada,
                id_curso_doc,
            ) = user

            participante = f"{nombre} {apellido}"
            curso = curso_nombre or ""
            docente_full = f"Dr(a). {docente or ''} {doc_ape or ''}".strip()
            documento = documento or 'doc'
            # Definir título y mensaje
            titulo = "CERTIFICADO\nIII TYAN Hands-on Schools en Bolivia 2025"
            if rol == 3:  # Estudiante
                if modalidad == "catedra-laboratorio" and nota and int(nota) > 64:
                    titulo = "CERTIFICADO DE APROBACION\nIII TYAN Hands-on Schools en Bolivia 2025"
                    mssg = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente_full}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
                else:
                    mssg = f"""Ha participado del curso de "{curso}" dictado por {docente_full}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
            elif rol == 2:  # Expositor
                curso = materia_dada or ""
                mssg = f"""Por su colaboración como ponente en el tema "{curso}". Realizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""

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
            pdf.multi_cell(600, 15, mssg, 0, "C")

            if rol == 3:
                pdf.set_font("Arial", "I", 14)
                pdf.set_text_color(0, 0, 0)
                pdf.set_xy(0, 510)
                pdf.multi_cell(600, 14, docente_full + " \nDocente de Materia", 0, "C")

                # Generar QR estudiante
                url = f"{os.getenv('URL_APP')}/cert/verificar/{id_inscripcion}-0"
                qr_img = segno.make(url)
                qr_path = os.path.join(folder, f"qr_{id_inscripcion}.png")
                qr_img.save(qr_path, scale=5)
                pdf.image(qr_path, x=740, y=500, w=80, h=80)

            elif rol == 2:
                # Generar QR expositor
                url = f"{os.getenv('URL_APP')}/cert/verificar/{id_usuario}-{id_curso_doc}"
                qr_img = segno.make(url)
                qr_path = os.path.join(folder, f"qr_{id_usuario}-{id_curso_doc}.png")
                qr_img.save(qr_path, scale=5)
                pdf.image(qr_path, x=740, y=500, w=80, h=80)

            file_name = f"{documento.replace(' ', '_')}_{participante.replace(' ', '_')}_{curso.replace(' ', '_')}_certificate.pdf"
            file_name = utils.sanitize_filename(file_name)
            output_path = os.path.join(folder, file_name)
            pdf.output(output_path)

            clean_email = email.replace('\xa0', '').strip()
            final_filename = file_name.replace('\xa0', ' ').strip()
            mensaje_limpio = mensaje.replace('\xa0', ' ').strip()
            
            if not clean_email:
                errores_envio.append((participante, "Correo electrónico vacío"))
                continue # Saltar esta iteración

            try:
                # 1. Crear el objeto EmailMessage
                msg_smtp = EmailMessage()
                # Usar el remitente forzado para evitar \xa0 en el campo From
                msg_smtp["From"] = f"{safe_sender_name} <{mail_address}>" 
                msg_smtp["To"] = clean_email
                msg_smtp["Subject"] = asunto 
                
                # 2. Definir el cuerpo del mensaje (limpio)
                msg_smtp.set_content(mensaje_limpio)
                
                # 3. Adjuntar el PDF generado
                with open(output_path, "rb") as f:
                    # Guess type para adjuntar
                    mime_type = mimetypes.guess_type(final_filename)[0] or 'application/pdf'
                    maintype, subtype = mime_type.split('/', 1)
                    
                    msg_smtp.add_attachment(f.read(), 
                                            maintype=maintype, 
                                            subtype=subtype, 
                                            filename=final_filename)
                                            
                # 4. Enviar usando SMTPLIB (Conexión segura SSL)
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(mail_address, app_password)
                    smtp.send_message(msg_smtp)
                
                # Si el envío fue exitoso
                exitos_envio.append(clean_email)
                
                # Actualizar DB (solo si rol == 3)
                if rol == 3:
                    with db.engine.begin() as conn_update:
                        conn_update.execute(
                            text("UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"),
                            {"id": id_inscripcion},
                        )
                        
            except Exception as e:
                errores_envio.append((clean_email, str(e)))


        shutil.rmtree(folder)

        flash(f"Certificados enviados a {len(exitos_envio)} usuarios.", "success")
        if errores_envio:
            flash(f"Errores al enviar a: {', '.join(e[0] for e in errores_envio)}", "error")

        return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

    # GET: mostrar formulario
    return render_template("Certificados/SendMuchosCertificados.html", rol_boton=rol_boton)



@certificate_bp.route("/verificar/<string:search>")
def verificar(search):
    partes = search.split("-")
    id_principal = int(partes[0])
    id_extra = int(partes[1])

    result = None
    tipo = None

    with db.engine.connect() as conn:
        if id_extra == 0:
            # Caso estudiante: buscamos por inscripcion
            tipo = "estudiante"
            query = text(
                """
                SELECT 
                    u.id_usuario,
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
                    cur.nombre as materia_dada,
                    cur.id_curso as id_curso_doc
                FROM usuarios u
                LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
                LEFT JOIN cursos c ON c.id_curso = i.id_curso
                LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
                LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
                LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
                WHERE i.id_inscripcion = :id_inscripcion
                LIMIT 1
            """
            )
            result = conn.execute(query, {"id_inscripcion": id_principal}).fetchone()
        else:
            # Caso docente
            tipo = "docente"
            query = text(
                """
                SELECT 
                    u.id_usuario,
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
                    cur.nombre as materia_dada,
                    cur.id_curso as id_curso_doc
                FROM usuarios u
                LEFT JOIN inscripciones i ON i.id_usuario = u.id_usuario
                LEFT JOIN cursos c ON c.id_curso = i.id_curso
                LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
                LEFT JOIN usuarios p ON p.id_usuario = c.id_ponente
                LEFT JOIN cursos cur ON cur.id_ponente = u.id_usuario
                WHERE u.id_usuario = :id_usuario
                AND cur.id_curso = :id_curso
                LIMIT 1
            """
            )
            result = conn.execute(
                query, {"id_usuario": id_principal, "id_curso": id_extra}
            ).fetchone()

    # Renderizamos resultados
    return render_template(
        "Certificados/verificar.html",
        existe=result is not None,
        certificado=result,
        tipo=tipo,
    )


@certificate_bp.route("/listar-certificados/<int:id_usuario>")
@login_required
@role_required(3)
def listar_certificados_estudiantes(id_usuario):
    inscripciones = utils.get_inscripciones(id_usuario)        
    return  render_template("Estudiante/certificados.html", inscripciones = inscripciones, id_usuario=id_usuario)

@certificate_bp.route("/listar-certificados-docente/<int:id_usuario>")
@login_required
@role_required(2)
def listar_certificados_docente(id_usuario):
    cursos = utils.get_cursos(id_usuario)
    return render_template(
        "Expositor/certificados.html", cursos=cursos, id_usuario=id_usuario
    )

def clean_text(text):
    if not text:
        return ""
    # Reemplazar espacios no separables y normalizar
    text = text.replace(u"\xa0", " ")
    return unicodedata.normalize("NFKC", text)