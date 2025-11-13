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
            "CERTIFICADO DE APROBACION"
            if row["modalidad"] == "catedra-laboratorio" and int(row["nota"]) > 64
            else "CERTIFICADO"
        )
        if (rol_boton) == 3:
            curso = row["curso_nombre"] or ""
            if row["modalidad"] == "catedra-laboratorio" and int(row["nota"]) > 64:
                mensaje = f"""Ha completado exitosamente el curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia)."""
            else:
                mensaje = f"""Ha participado del curso de "{curso}" dictado por {docente}, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'."""
        elif (rol_boton) == 2:
            curso = row["materia_dada"] or ""
            # mensaje = f"""Por su colaboración como ponente en el tema  "{curso}".\nRealizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés."""
            mensaje = "In recognition of their active involvement in the third TYAN Hands-On Schools conference, and their contribution of significant knowledge and experience for the enhancement of the program for all participants. The event took place at the Universidad Mayor de San Andrés in La Paz, Bolivia, from 6th to 10th October 2025."
        # fecha = date.today()

        pdf = FPDF(orientation="L", unit="pt", format="A4")
        pdf.add_page()
        template_path = os.path.join(base_dir, "Input", "certificate_template.png")
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

        # Registrar la fuente (asumiendo que están en ./fonts/)
        fonts_path_poppins_bold = os.path.join(base_dir, "fonts", "Poppins-Bold.ttf")
        fonts_path_poppins_medium = os.path.join(base_dir, "fonts", "Poppins-Medium.ttf")
        fonts_path_poppins_regular= os.path.join(base_dir, "fonts", "Poppins-Regular.ttf")
        fonts_path_poppins_light= os.path.join(base_dir, "fonts", "Poppins-Light.ttf")
        pdf.add_font("Poppins_Bold", "", fonts_path_poppins_bold, uni=True)
        pdf.add_font("Poppins_Medium", "", fonts_path_poppins_medium, uni=True)
        pdf.add_font("Poppins_Regular", "", fonts_path_poppins_regular, uni=True)
        pdf.add_font("Poppins_Light", "", fonts_path_poppins_light, uni=True)

        pdf.set_font("Poppins_Bold", style="", size=50)
        pdf.set_text_color(0, 20, 60)
        pdf.set_xy(0, 125)
        pdf.multi_cell(842, 60, titulo, 0, "C")

        pdf.set_font("Poppins_Light", style="", size=15)
        pdf.set_xy(0, 175)
        pdf.multi_cell(842, 60, "The organization in charge of TYAN BOLIVIA awarded this recognition to:", 0, "C")

        pdf.set_font("Poppins_Bold", "", 30)
        pdf.set_xy(0, 225)
        pdf.cell(w=842, h=60, txt=participante.upper(), align="C")

        ### EL SIGUIENTE BLOQUE ES LA LINEA HORIZONTAL
        # Configuración
        margen_horizontal = 120   # distancia desde los bordes izquierdo y derecho
        y_pos = 280              # altura donde irá la línea (en mm)
        color_linea = (0, 119, 194)  # azul medio (RGB)

        # Dibujar línea
        pdf.set_draw_color(*color_linea)
        pdf.set_line_width(0.5)  # grosor opcional

        # Coordenadas calculadas
        x1 = margen_horizontal
        x2 = pdf.w - margen_horizontal  # ancho total - margen derecho

        pdf.line(x1, y_pos, x2, y_pos)
        ### FIN DE LA LINEA HORIZONTAL


        pdf.set_font("Poppins_Light", "", 13)
        pdf.set_xy((pdf.w - 600) / 2, 300)
        pdf.multi_cell(w=600, h=20, txt=mensaje, border=0, align="J")
        
        x = 50
        pdf.set_font("Poppins_Light", "", 13)
        pdf.set_xy(x, 425)
        pdf.multi_cell(w=150, h=10, txt="Dr. Max Paoli", align="C")
        pdf.set_font("Poppins_Medium","", 13)
        pdf.set_xy(x, 440)
        pdf.multi_cell(w=150, h=10, txt="Director", align="C")
        pdf.set_xy(x, 455)
        pdf.multi_cell(w=150, h=10, txt="Programa TYAN", align="C")

        x = 200
        pdf.set_font("Poppins_Light", "", 13)
        pdf.set_xy(x, 425)
        pdf.multi_cell(w=150, h=10, txt="Dr. Rigoberto Choque", align="C")
        pdf.set_font("Poppins_Medium","", 13)
        pdf.set_xy(x, 440)
        pdf.multi_cell(w=150, h=10, txt="Director Académico", align="C")
        pdf.set_xy(x, 455)
        pdf.multi_cell(w=150, h=10, txt="Carrera Cs. Quimicas", align="C")

        x = 350
        pdf.set_font("Poppins_Light", "", 13)
        pdf.set_xy(x, 425)
        pdf.multi_cell(w=150, h=10, txt="Dra. Leslie Tejada", align="C")
        pdf.set_font("Poppins_Medium","", 13)
        pdf.set_xy(x, 440)
        pdf.multi_cell(w=150, h=10, txt="Coordinadora", align="C")
        pdf.set_xy(x, 455)
        pdf.multi_cell(w=150, h=10, txt="TYAN-TWAS", align="C")

        x = 500
        pdf.set_font("Poppins_Light", "", 13)
        pdf.set_xy(x, 425)
        pdf.multi_cell(w=300, h=10, txt="M.Sc. Aldo Valdez Alvarado", align="C")
        pdf.set_font("Poppins_Medium","", 13)
        pdf.set_xy(x, 440)
        pdf.multi_cell(w=300, h=10, txt="Decano", align="C")
        pdf.set_xy(x, 455)
        pdf.multi_cell(w=300, h=10, txt="Facultado de Ciencias Puras y Naturales", align="C")

        pdf.set_font("Poppins_Light", "", 10 )
        pdf.set_xy(600, 470)
        pdf.multi_cell(w=200, h=10, txt="La Paz - Bolivia, Octubre de 2025")

        ### FIRMAS DIGITALES
        img_path = os.path.join(base_dir, "Input", "firma_max_paoli_sin_fondo.png")
        pdf.image(img_path, 50, 380, w=149, h=70)

        img_path = os.path.join(base_dir, "Input", "firma_decano.png")
        pdf.image(img_path, 550, 340, w=207, h=120)
        ### FIN DE FIRMAS DIGITALES

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

# "Modelos animales y aplicaciones en agroindustria y medio ambiente/ Animal Models in Agriculture and Environmental Research"
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

        # Obtener usuarios según rol
        with db.engine.connect() as conn:
            query = """
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
                    c.id_curso as id_curso,
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
            result = conn.execute(text(query), {"rol_boton": rol_boton})
            participants = pd.DataFrame(result.fetchall(), columns=result.keys())

        if participants.empty:
            flash("No hay usuarios para este rol.", "warning")
            return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

        errores_envio, exitos_envio = [], []

        # Configuración de correo SMTP
        mail_address = os.getenv("MAIL_USERNAME").replace('\xa0', '').strip()
        app_password = os.getenv("MAIL_PASSWORD")
        safe_sender_name = "TYAN Bolivia"
        
        traducciones = {
            "Biofertilizantes para la producción sostenible de cultivos": "Biofertilizers for Sustainable Crop Production",
            "Agroinnovación para construir resiliencia: modelos gastronómicos sostenibles y saludables": "Agroinnovation to Build Resilience: Sustainable and Healthy Gastronomic Models",
            "Algas para la seguridad alimentaria y nutricional": "Algae for Food and Nutritional Security",
            "Fitomejoradores biología para la reproducción vegetal": "Plant Breeders: Biology for Plant Reproduction",
            "Modelos animales y aplicaciones en agroindustria y medio ambiente": "Animal Models and Applications in Agroindustry and the Environment"
        }
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(mail_address, app_password)
            
            for _, row in participants.iterrows():
                participante = f"{row['nombre']} {row['apellido']}"
                email = (row["email"] or "").strip()
                if not email:
                    errores_envio.append((participante, "Correo vacío"))
                    continue
                
                nota = float(row["nota"]) if row["nota"] not in (None, "", "NaN") else 0
                if nota <= 1:
                    continue   

                
                documento = row["documento"] or "CERT"
                docente = f"{row['docente'] or ''} {row['doc_ape'] or ''}".strip()
                curso = ""
                
                titulo = (
                    "CERTIFICATE OF PARTICIPATION"
                    if row["nota"] and int(row["nota"]) > 64
                    else "CERTIFICATE OF PARTICIPATION"
                )

                
                
                # Mensaje del certificado
                if (rol_boton) == 3:
                    curso = row["curso_nombre"] or ""
                    curso_traducido = traducciones.get(curso, curso)  # si no existe traducción, deja el original
                    print(row["nota"])
                    if row["nota"] and int(row["nota"]) > 64:
                        
                        mensaje_cert = f"""Has approved the course ""{curso_traducido}", delivered by Dr. {docente}, within the framework of the Third Edition of the TYAN-TWAS Hands-on Schools in Bolivia, 2025.\nThe course comprised a total of 30 academic hours, corresponding to 1 CLAR (Latin American Reference Credit), and was conducted in La Paz, Bolivia, from 6 to 10 October 2025."""
                    else:
                        mensaje_cert = f"""Has participed the course ""{curso_traducido}", delivered by Dr. {docente}, within the framework of the Third Edition of the TYAN-TWAS Hands-on Schools in Bolivia, 2025.\nThe course comprised a total of 30 academic hours, corresponding to 1 CLAR (Latin American Reference Credit), and was conducted in La Paz, Bolivia, from 6 to 10 October 2025."""
                elif (rol_boton) == 2:
                    curso = row["materia_dada"] or ""
                    mensaje_cert = "In recognition of their active involvement in the third TYAN Hands-On Schools conference, and their contribution of significant knowledge and experience for the enhancement of the program for all participants. The event took place at the Universidad Mayor de San Andrés in La Paz, Bolivia, from 6th to 10th October 2025."

                # Crear PDF con el mismo formato
                pdf = FPDF(orientation="L", unit="pt", format="A4")
                pdf.add_page()

                # Fondo
                template_path = os.path.join(base_dir, "Input", "certificate_template.png")
                pdf.image(template_path, 0, 0, w=842, h=595)

                # Registrar fuentes
                pdf.add_font("Poppins_Bold", "", os.path.join(base_dir, "fonts", "Poppins-Bold.ttf"), uni=True)
                pdf.add_font("Poppins_Medium", "", os.path.join(base_dir, "fonts", "Poppins-Medium.ttf"), uni=True)
                pdf.add_font("Poppins_Regular", "", os.path.join(base_dir, "fonts", "Poppins-Regular.ttf"), uni=True)
                pdf.add_font("Poppins_Light", "", os.path.join(base_dir, "fonts", "Poppins-Light.ttf"), uni=True)

                pdf.set_font("Poppins_Bold", size=40)
                pdf.set_text_color(0, 20, 60)
                pdf.set_xy(0, 125)
                pdf.multi_cell(842, 60, titulo, 0, "C")

                pdf.set_font("Poppins_Light", size=15)
                pdf.set_xy(0, 155)
                pdf.multi_cell(842, 60, "The organization in charge of TYAN BOLIVIA awarded this recognition to:", 0, "C")

                pdf.set_font("Poppins_Bold", size=30)
                pdf.set_xy(0, 185)
                pdf.cell(842, 60, participante.upper(), align="C")

                # Línea decorativa
                margen_horizontal = 120
                y_pos = 240
                pdf.set_draw_color(0, 119, 194)
                pdf.set_line_width(0.5)
                pdf.line(margen_horizontal, y_pos, pdf.w - margen_horizontal, y_pos)

                pdf.set_font("Poppins_Light", size=11)
                pdf.set_xy((pdf.w - 600) / 2, 260)
                pdf.multi_cell(600, 20, mensaje_cert, 0, "J")

                # Modelos animales y aplicaciones en agroindustria y medio ambiente
                # coordenadas[50, 200, 350, 500], [40, 160. 280, 400, 500]
                # coordenadas[80, 280, 80], [50, 200, 350, 500]
                if curso != "Modelos animales y aplicaciones en agroindustria y medio ambiente":    
                    # Firmas y texto inferior
                    
                    size = 11
                    x = 40
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(150, 10, "Dr. Max Paoli", align="C")
                    pdf.set_font("Poppins_Medium", "", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(150, 10, "Director", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(150, 10, "TYAN Program", align="C")
                    
                    x = 160
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(w=150, h=10, txt="Dr. Rigoberto Choque", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(w=150, h=10, txt="Academic Director", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(w=150, h=10, txt="Department of Chemical Sciences", align="C")
                    
                    x = 280
                    docente_x = x
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(w=150, h=10, txt=f"Dr. {docente}", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(w=150, h=10, txt="Course Lecturer", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(w=150, h=10, txt="TYAN-TWAS", align="C")
                    
                    x = 400
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(w=150, h=10, txt="Dra. Leslie Tejada", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(w=150, h=10, txt="Coordinator", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(w=150, h=10, txt="TYAN-TWAS", align="C")
                    
                    x = 500
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(300, 10, "M.Sc. Aldo Valdez Alvarado", align="C")
                    pdf.set_font("Poppins_Medium", "", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(300, 10, "Dean", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(300, 10, "Faculty of Pure and Natural Sciences", align="C")

                    pdf.set_font("Poppins_Light", "", 10)
                    pdf.set_xy(600, 470)
                    pdf.multi_cell(200, 10, "La Paz - Bolivia, October 2025")

                    # Firmas digitales
                    pdf.image(os.path.join(base_dir, "Input", "firma_max_paoli_sin_fondo.png"), 40, 380, w=134, h=63)
                    pdf.image(os.path.join(base_dir, "Input", "choque_firma.png"), 170, 350, w=120*0.8, h=89*0.8)
                    pdf.image(os.path.join(base_dir, "Input", "tejada_firma.png"), 400, 350, w=182*0.8, h=123*0.8)
                    pdf.image(os.path.join(base_dir, "Input", "firma_decano.png"), 550, 370, w=207*0.8, h=120*0.8)

                    if curso=="Biofertilizantes para la producción sostenible de cultivos": pdf.image(os.path.join(base_dir, "Input", "warshi_firma.png"), docente_x+20, 370, w=116, h=70)
                    if curso=="Agroinnovación para construir resiliencia: modelos gastronómicos sostenibles y saludables": pdf.image(os.path.join(base_dir, "Input", "izurieta_firma.png"), docente_x, 360, w=180, h=96)
                    if curso=="Algas para la seguridad alimentaria y nutricional": pdf.image(os.path.join(base_dir, "Input", "ambati_firma.png"), docente_x, 390, w=128, h=27)
                    if curso=="Fitomejoradores biología para la reproducción vegetal": pdf.image(os.path.join(base_dir, "Input", "bolaños_firma.png"), docente_x, 370, w=177, h=63)
                    # if curso=="Fitomejoradores biología para la reproducción vegetal": 
                    #     pdf.image(os.path.join(base_dir, "Input", "bolaños_firma.png"), docente_x, 370, w=177, h=63)
                    #     pdf.image(os.path.join(base_dir, "Input", "ambati_firma.png"), docente_x, 390, w=128, h=27)
                    #     pdf.image(os.path.join(base_dir, "Input", "izurieta_firma.png"), docente_x, 360, w=180, h=96)
                    #     pdf.image(os.path.join(base_dir, "Input", "warshi_firma.png"), docente_x+20, 370, w=116, h=70)

                else:
                    size = 10
                    y = 425
                    x = 50
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, y)
                    pdf.multi_cell(w=150, h=10, txt="Dr. Max Paoli", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, y+15)
                    pdf.multi_cell(w=150, h=10, txt="Director", align="C")
                    pdf.set_xy(x, y+30)
                    pdf.multi_cell(w=150, h=10, txt="Programa TYAN", align="C")

                    x = 200
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, 425)
                    pdf.multi_cell(w=150, h=10, txt="Dr. Rigoberto Choque", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, 440)
                    pdf.multi_cell(w=150, h=10, txt="Director Académico", align="C")
                    pdf.set_xy(x, 455)
                    pdf.multi_cell(w=150, h=10, txt="Carrera Cs. Quimicas", align="C")

                    x = 350
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, y)
                    pdf.multi_cell(w=150, h=10, txt="Dra. Leslie Tejada", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, y+15)
                    pdf.multi_cell(w=150, h=10, txt="Coordinadora", align="C")
                    pdf.set_xy(x, y+30)
                    pdf.multi_cell(w=150, h=10, txt="TYAN-TWAS", align="C")

                    x = 500
                    pdf.set_font("Poppins_Light", "", size)
                    pdf.set_xy(x, y)
                    pdf.multi_cell(w=300, h=10, txt="M.Sc. Aldo Valdez Alvarado", align="C")
                    pdf.set_font("Poppins_Medium","", size)
                    pdf.set_xy(x, y+15)
                    pdf.multi_cell(w=300, h=10, txt="Decano", align="C")
                    pdf.set_xy(x, y+30)
                    pdf.multi_cell(w=300, h=10, txt="Facultado de Ciencias Puras y Naturales", align="C")

                    pdf.set_font("Poppins_Light", "", 10)
                    pdf.set_xy(600, 470)
                    pdf.multi_cell(200, 10, "La Paz - Bolivia, Octubre de 2025")

                    # Firmas digitales
                    pdf.image(os.path.join(base_dir, "Input", "firma_max_paoli_sin_fondo.png"), 50, 380, w=149, h=70)
                    pdf.image(os.path.join(base_dir, "Input", "choque_firma.png"), 220, 350, w=120*0.8, h=89*0.8)
                    pdf.image(os.path.join(base_dir, "Input", "tejada_firma.png"), 350, 350, w=182*0.8, h=123*0.8)
                    pdf.image(os.path.join(base_dir, "Input", "firma_decano.png"), 550, 370, w=207*0.8, h=120*0.8)
                    

                # QR
                if rol_boton == 3:
                    qr_url = f"{os.getenv('URL_APP')}/cert/verificar/{row['id_inscripcion']}-0"
                    qr_path = os.path.join(folder, f"qr_{row['id_inscripcion']}.png")
                else:
                    qr_url = f"{os.getenv('URL_APP')}/cert/verificar/{row['id_usuario']}-{row['id_curso_doc']}"
                    qr_path = os.path.join(folder, f"qr_{row['id_usuario']}-{row['id_curso_doc']}.png")

                qr_img = segno.make(qr_url)
                qr_img.save(qr_path, scale=5)
                pdf.image(qr_path, 740, 500, w=80, h=80)

                # Guardar archivo PDF
                file_name = utils.sanitize_filename(f"{documento}_{participante}_{curso}_certificate.pdf")
                pdf_path = os.path.join(folder, file_name)
                pdf.output(pdf_path)

                # Enviar correo
                try:
                    msg = EmailMessage()
                    msg["From"] = f"{safe_sender_name} <{mail_address}>"
                    msg["To"] = email
                    # msg["bcc"] = "lktejeda@umsa.bo"
                    msg["Subject"] = asunto
                    msg.set_content(mensaje)

                    with open(pdf_path, "rb") as f:
                        mime_type = mimetypes.guess_type(file_name)[0] or "application/pdf"
                        maintype, subtype = mime_type.split("/", 1)
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=file_name)
        
                    smtp.send_message(msg)

                    exitos_envio.append(email)  

                    # Actualizar estado si es estudiante
                    if rol_boton == 3:
                        with db.engine.begin() as conn_update:
                            conn_update.execute(
                                text("UPDATE inscripciones SET certificado_generado = TRUE WHERE id_inscripcion = :id"),
                                {"id": row["id_inscripcion"]},
                            )

                except Exception as e:
                    errores_envio.append((email, str(e)))

        try:
            shutil.rmtree(folder)
        except Exception as e:
            print(f"Error al eliminar carpeta temporal: {e}")


        flash(f"Certificados enviados a {len(exitos_envio)} usuarios.", "success")
        if errores_envio:
            flash(f"Errores al enviar a: {', '.join(e[0] for e in errores_envio)}", "danger")

        return redirect(url_for("certificate.enviar_certificados_todos", rol_boton=rol_boton))

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