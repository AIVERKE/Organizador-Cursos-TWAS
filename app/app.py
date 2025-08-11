from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


# Página de inicio
@app.route("/")
def index():
    return render_template("index.html")


# Página de login
@app.route("/login")
def login():
    return render_template("login.html")


# Forgot password
@app.route("/forgot-password")
def forgot_password():
    return render_template("ForgotPassword/ForgotPassword.html")


@app.route("/forgot-password-alert")
def forgot_password_alert():
    return render_template("ForgotPassword/ForgotPasswordAlert.html")


# ¡Este se abre solo desde un enlace! Ignoramos ruta directa
# @app.route('/forgot-password-verificado')
# def forgot_password_verificado():
#     return render_template('ForgotPassword/ForgotPasswordverificado.html')

# ========== VISTAS PARA ESTUDIANTE ==========


@app.route("/estudiante")
def estudiante():
    return render_template("Estudiante/Estudiante.html")


@app.route("/estudiante/curso")
def estudiante_curso():
    return render_template("Estudiante/Curso.html")


# ========== VISTAS PARA EXPOSITOR ==========


@app.route("/expositor")
def expositor():
    return render_template("Expositor/expositor.html")


@app.route("/expositor/datos-personales")
def expositor_datos():
    return render_template("Expositor/datosPersonalesExp.html")


@app.route("/expositor/curso")
def expositor_curso():
    return render_template("Expositor/CursoExp.html")


@app.route("/expositor/calificaciones")
def expositor_calificaciones():
    return render_template("Expositor/calificacionExp.html")


# ========== VISTA DE DASHBOARD (opcional) ==========
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ========== Run App ==========
if __name__ == "__main__":
    app.run(debug=True)
