from flask import Flask
from dotenv import load_dotenv
from .extensions import db, mail
from flask_login import LoginManager
from app.models.user import Usuario  # Si da problemas, mueve esto dentro de load_user
from app.config import (
    DevConfig,
)  # Puedes cambiar a ProdConfig o TestConfig según tu entorno


def create_app(config_class=DevConfig):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)  # Cargamos toda la configuración centralizada

    # Inicializar extensiones
    db.init_app(app)
    mail.init_app(app)

    # Registrar blueprints
    ## Autenticador (Forgot my password)
    from app.api.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    ## Generador de qr
    from app.api.qrs import qrs_bp

    app.register_blueprint(qrs_bp, url_prefix="/qrs")

    # Página principal index
    from app.api.home import home_bp

    app.register_blueprint(home_bp, url_prefix="/")

    # CRUD Usuarios
    from app.api.usuarios import usuario_bp

    app.register_blueprint(usuario_bp, url_prefix="/usuarios")

    # CRUD eventos y version_evento
    from app.api.eventos import evento_bp

    app.register_blueprint(evento_bp, url_prefix="/eventos")

    # CRUD Cursos
    from app.api.cursos import curso_bp

    app.register_blueprint(curso_bp, url_prefix="/cursos")

    # CRUD Inscripcion
    from app.api.inscripciones import ins_bp

    app.register_blueprint(ins_bp, url_prefix="/ins")


    ## Generador de certificados
    from app.api.certificate import certificate_bp

    app.register_blueprint(certificate_bp, url_prefix="/cert")

    ## Lectura archivos tipo excel o similares
    from app.api.rxls import rxls_bp

    app.register_blueprint(rxls_bp, url_prefix="/rxls")

    # Escaner QR's
    from app.api.qrscan import qrscan_bp

    app.register_blueprint(qrscan_bp, url_prefix="/scan")

    # Rutas Coordinador
    from app.api.coordinador import coordinador_bp

    app.register_blueprint(coordinador_bp, url_prefix="/coordinador")

    # Rutas Ponente
    from app.api.ponente import ponente_bp

    app.register_blueprint(ponente_bp, url_prefix="/ponente")

    # Configurar Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    # Importacion de modelos
    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Crear las tablas necesarias en la base de datos
    with app.app_context():
        db.create_all()
    print("\n[RUTAS REGISTRADAS EN FLASK]:")
    for rule in app.url_map.iter_rules():
        print(rule)

    return app
