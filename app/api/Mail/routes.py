from flask import Blueprint, request, jsonify, current_app
import smtplib
from email.message import EmailMessage
import os
from threading import Thread
import mimetypes
from app.controllers import u_controller as usu
from . import mail_bp as email_bp
from flask_login import login_required
from app.api.auth.utils import role_required
import time

def send_emails_in_background(subject, body, file, estudiantes, sender, app_password, qr_folder):
    batch_size = 10  # cantidad de correos por lote
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        for i in range(0, len(estudiantes), batch_size):
            batch = estudiantes[i:i + batch_size]
            for est in batch:
                email = est["email"]
                insc_id = est["id_inscripcion"]

                new_body = "ESTUDIANTE: " + est["nombre"] + "\n" + "CURSO: " + est["curso"] + "\n" + body

                msg = EmailMessage()
                msg["From"] = f"TYAN <{sender}>"
                msg["To"] = email
                msg["bcc"] = "lktejeda@umsa.bo"
                msg["Subject"] = subject
                #msg.set_content(body)
                msg.set_content(new_body)

                # Adjuntar QR si existe
                qr_file_path = None
                if os.path.isdir(qr_folder):
                    qrs_usuario = [
                        f for f in os.listdir(qr_folder)
                        if f.startswith(f"qr_{insc_id}_") and f.endswith(".png")
                    ]
                    if qrs_usuario:
                        qrs_usuario.sort(reverse=True)
                        qr_file_path = os.path.join(qr_folder, qrs_usuario[0])
                if qr_file_path and os.path.exists(qr_file_path):
                    mime = mimetypes.guess_type(qr_file_path)[0] or "image/png"
                    maintype, subtype = mime.split("/", 1)
                    with open(qr_file_path, "rb") as f:
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(qr_file_path))

                # Adjuntar archivo enviado por el usuario
                if file and file.filename:
                    mimetype = file.mimetype or 'application/octet-stream'
                    maintype, subtype = mimetype.split('/',1)
                    msg.add_attachment(file.read(), maintype=maintype, subtype=subtype, filename=file.filename)

                smtp.send_message(msg)

            # Pausa corta entre lotes para no saturar Gmail
            #time.sleep(5)

@email_bp.route("/", methods=["POST"])
@login_required
@role_required(1, 4)
def send_email():
    # Determinar si el request es form-data o JSON
    if request.content_type and "multipart/form-data" in request.content_type.lower():
        subject = request.form.get("asunto")
        body = request.form.get("contenido")
        file = request.files.get("imagen")
    else:
        data = request.get_json(silent=True) or {}
        subject = data.get("subject")
        body = data.get("body")
        file = None

    if not subject or not body:
        return jsonify({"error": "Faltan asunto o contenido"}), 400

    sender = os.environ.get("MAIL_USERNAME")
    app_password = os.environ.get("MAIL_PASSWORD")

    # Traer estudiantes pendientes de notificación
    estudiantes = [e for e in usu.obtener_estudiantes_i() if e.get("email")]

    if not estudiantes:
        return jsonify({"message": "No hay estudiantes pendientes de notificación"}), 200

    qr_folder = os.path.join(current_app.root_path, "static", "qrs")

    # Enviar correos de manera sincrónica
    send_emails_in_background(subject, body, file, estudiantes, sender, app_password, qr_folder)

    # Marcar estudiantes como notificados
    ids = [e["id_usuario"] for e in estudiantes]
    usu.marcar_notificados(ids)

    # Respuesta al usuario
    return jsonify({"message": "Los correos se enviaron correctamente y los estudiantes fueron notificados"})
