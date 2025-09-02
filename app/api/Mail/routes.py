from flask import Blueprint, request, jsonify
import smtplib
from email.message import EmailMessage
from . import mail_bp as email_bp
@email_bp.route("/send-email", methods=["POST"])
def send_email():
    data = request.json
    subject = data.get("subject")
    body = data.get("body")

    # Configuración
    sender = "alanarielmaldonadocarvajal1@gmail.com"
    app_password = "fhzy qcdf jvyw vqbk"
    recipients = ["alanmaldonadoc5@gmail.com", "alan.maldonado@ucb.edu.bo"]

    # Crear mensaje
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    # Adjuntar imagen de prueba
    with open("static/ramires.jpeg", "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename="ramires.jpeg"
        )

    # Enviar
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)

    return jsonify({"message": "Correo enviado con éxito ✅"})
