from flask import Blueprint, request, jsonify, current_app
import smtplib
from email.message import EmailMessage
import os
from app.controllers import u_controller as usu #para el traer todos los correos
from . import mail_bp as email_bp
import time

@email_bp.route("/", methods=["POST"])
def send_email():
    data = request.json
    subject = data.get("subject")
    body = data.get("body")

    # Configuración
    sender = os.environ.get("MAIL_USERNAME")  #correo en .env
    app_password = os.environ.get("MAIL_PASSWORD")  # contraseña de aplicación en .env
    estudiantes = usu.obtener_estudiantes()
    recipients = [e["email"] for e in estudiantes if e.get("email")]
    #recipients = ["alanmaldonadoc5@gmail.com", "alan.maldonado@ucb.edu.bo"]
    #se puede enviar a dos por minuto en caso de 200 correos
    batch_size = 1

    for i in range (0, len(recipients), batch_size):
        batch = recipients[i:i + batch_size]
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = ", ".join(batch)
        msg["Subject"] = subject
        msg.set_content(body)
        file_path = os.path.join(current_app.root_path, "static", "ramires.jpeg")
        with open(file_path, "rb") as f:
            msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename="ramires.jpeg"
            )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        print("Correo Enviado 👁👄👁💅") #imprime en consola cada que se envió un correo
        time.sleep(10)
    return jsonify({"message": "Correos enviados con éxito ✅"}) #se muestra al final de los envíos, de momento tardaria 20 segundos en aparecer ya que debe enviar dos correos con 10 segundos de diferencia entre ellos para completar de ejecutar la función.
        



    # Crear mensaje
    

    # ✅ Construir ruta absoluta al archivo en static
    

    

    # Enviar
    



