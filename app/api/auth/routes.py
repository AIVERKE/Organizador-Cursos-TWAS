# Importamos las librerias de flask necesarias para renderizar los templates html
from flask import render_template, request, redirect, url_for, flash, session

# Seguridad de las contraseñas y comparar las mismas
from werkzeug.security import check_password_hash, generate_password_hash

# Traemos el blueprint creado en __init__.py
from . import auth_bp

# Importamos el modelo usuario de SQLAlchemy
from app.models.user import db, Usuario

# Impotamos las funciones útiles para forgot my password
from .utils import send_reset_email, verify_reset_token, role_required

# Importamos librerias para trabajar con el login
from flask_login import login_user, logout_user, login_required, current_user


# Creamos la ruta a la debe dirigirnos el blueprint
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        contrasena = request.form["contrasena"]
        recuerdame = request.form.get("recuerdame") == "on"

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.contrasena, contrasena):
            login_user(user, remember=recuerdame)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Usuario y/o contraseña invalidos", "danger")

    return render_template("login.html")


@auth_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required(1, 2, 3, 4)
def dashboard():
    from app.controllers import u_controller as est

    user_data = est.obtener_estudiante(current_user.id_usuario)
    if current_user.id_rol == 1:
        return render_template(
            "Coordinador/indexCoordinador.html",
            nombre=current_user.nombre,
            apellidos=current_user.apellido,
        )
    if current_user.id_rol == 2:
        return render_template(
            "Expositor/expositor.html",
            nombre=current_user.nombre,
            apellidos=current_user.apellido,
        )
    if current_user.id_rol == 3:
        return redirect(
            url_for("qrs.perfil_estudiante", id_usuario=current_user.id_usuario)
        )
    return "Inicio de sesión como desarrollador tienes acceso a todos los links"


# vista creada para obtener cursos inscritos del estudiante 31/04/2025 10:05 pm


@auth_bp.route("/estudiante/cursos")
@login_required
@role_required(3)
def cursos_estudiante():
    from app.controllers import i_controller as ins
    from app.controllers import c_controller as cursos

    id_usuario = current_user.id_usuario
    inscripciones = ins.obtener_inscripciones_por_usuario(id_usuario)
    # Extrae los cursos desde las inscripciones
    lista_cursos = []
    for insc in inscripciones:
        curso_dict = {"nombre": insc[2], "descripcion": insc[3], "modalidad": insc[4]}
        lista_cursos.append(curso_dict)

    return render_template("Estudiante/Curso.html", cursos=lista_cursos)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            user = Usuario.query.filter_by(email=email).first()
            if user:
                send_reset_email(user)
            else:
                print("No se encontró un usuario")
        else:
            print("No se encontró el email.")
        flash(
            "Si el correo existe, se enviará un enlace para restablecer la contraseña.",
            "info",
        )
        return redirect(url_for("auth.forgot_password_alert"))

    return render_template("ForgotPassword/ForgotPassword.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_token(token):
    email = verify_reset_token(token)
    if not email:
        flash("El enlace es inválido o ha expirado.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = Usuario.query.filter_by(email=email).first_or_404()

    if request.method == "POST":
        nueva = request.form.get("new_password")
        confirmar = request.form.get("confirm_password")

        if not nueva or not confirmar:
            flash("Por favor completa ambos campos.", "warning")
        elif nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
        else:
            user.contrasena = generate_password_hash(nueva)
            db.session.commit()
            flash("¡Tu contraseña ha sido actualizada!", "success")
            return redirect(url_for("auth.login"))

    return render_template("ForgotPassword/ResetPassword.html", token=token)


@auth_bp.route("forgot-password-alert", methods=["GET", "POST"])
def forgot_password_alert():
    return render_template("ForgotPassword/ForgotPasswordAlert.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for("auth.login"))
