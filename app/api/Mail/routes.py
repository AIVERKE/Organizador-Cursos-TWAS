from flask import Blueprint, request, jsonify, current_app
import smtplib
from email.message import EmailMessage
import os
from app.controllers import u_controller as usu #para el traer todos los correos
from . import mail_bp as email_bp
import time
from flask_login import login_required
from app.api.auth.utils import role_required


import mimetypes

@email_bp.route("/", methods=["POST"])
@login_required
@role_required(1,4)
def send_email():
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
    
    # Configuración
    sender = os.environ.get("MAIL_USERNAME")  #correo en .env
    app_password = os.environ.get("MAIL_PASSWORD")  # contraseña de aplicación en .env
    estudiantes = usu.obtener_estudiantes_i()
    
    estudiantes = [e for e in estudiantes if e.get("email")]  # Filtrar solo los que tienen correo
    qr_folder = os.path.join(current_app.root_path, "static", "qrs")
    
    
    recipients = [e["email"] for e in estudiantes if e.get("email")]
    
    
    #recipients = ["alanmaldonadoc5@gmail.com", "alan.maldonado@ucb.edu.bo"]
    #se puede enviar a dos por minuto en caso de 200 correos
    batch_size = 1 #número de correos por lote


    for i in range (0, len(estudiantes), batch_size):
        batch = estudiantes[i:i + batch_size]
        for est in batch:
            email = est["email"]
            insc_id = est["id_inscripcion"]

            msg = EmailMessage()
            msg["From"] = sender
            msg["To"] = email
            msg["Subject"] = subject
            msg.set_content(body)

            qr_file_path = None
            if os.path.isdir(qr_folder):
                qrs_usuario = [
                    f for f in os.listdir(qr_folder)
                    if f.startswith(f"qr_{insc_id}_") and f.endswith(".png")
                ]
                if qrs_usuario:
                    # elegir el más reciente (por timestamp en el nombre)
                    qrs_usuario.sort(reverse=True)
                    qr_file_path = os.path.join(qr_folder, qrs_usuario[0])

            if qr_file_path and os.path.exists(qr_file_path):
                mime = mimetypes.guess_type(qr_file_path)[0] or "image/png"
                maintype, subtype = mime.split("/", 1)
                with open(qr_file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(qr_file_path)
                    )
            else:
                print(f"No se encontró QR para inscripción {insc_id}")

        '''
        file_path = os.path.join(current_app.root_path, "static", "ramires.jpeg")
        with open(file_path, "rb") as f:
            msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename="ramires.jpeg"
            )
        '''


        if file and file.filename:
            mimetype = file.mimetype or 'application/octet-stream' 
            maintype, subtype = mimetype.split('/',1)
            msg.add_attachment(
                file.read(),
                maintype=maintype,
                subtype=subtype,
                filename=file.filename
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        print(f"Correo Enviado a {batch} con QR de inscripcion {insc_id}") #imprime en consola cada que se envia un correo
        time.sleep(10)
    return jsonify({"message": "Correos enviados con éxito"}) #se muestra al final de los envíos, de momento tardaria 20 segundos en aparecer ya que debe enviar dos correos con 10 segundos de diferencia entre ellos para completar de ejecutar la función.
