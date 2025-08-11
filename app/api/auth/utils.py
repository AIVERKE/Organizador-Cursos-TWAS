from flask import url_for, redirect, render_template
from flask_login import current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app import mail
from functools import wraps
import os


def get_serializer():
    return URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def get_reset_token(user_email):
    serializer = get_serializer()
    return serializer.dumps(user_email, salt="password-reset-salt")


def verify_reset_token(token, max_age=3600):
    serializer = get_serializer()
    try:
        return serializer.loads(token, salt="password-reset-salt", max_age=max_age)
    except Exception:
        return None


def send_reset_email(user):
    token = get_reset_token(user.email)
    reset_url = url_for("auth.reset_token", token=token, _external=True)

    msg = Message(
        "Password Reset Request", sender="noreply@yourapp.com", recipients=[user.email]
    )
    msg.body = f"Reset your password: {reset_url}"
    mail.send(msg)
    print(f"[DEBUG] Enviaríamos este link a {user.email}: {reset_url}")


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth_bp.login"))
            if current_user.id_rol not in roles:
                return render_template("Answers/no-found403.html")
            return f(*args, **kwargs)

        return decorated_function

    return wrapper
