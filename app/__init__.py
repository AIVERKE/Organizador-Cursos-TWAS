from flask import Flask, request, g
from dotenv import load_dotenv
from .extensions import db, mail
from flask_login import LoginManager
from app.models.user import Usuario
from app.config import DevConfig
import time
import logging


def create_app(config_class=DevConfig):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    mail.init_app(app)

    # Lista para evitar registrar el mismo blueprint dos veces
    registered_blueprints = set()

    def safe_register(bp, prefix):
        if bp.name in registered_blueprints:
            print(
                f"[ADVERTENCIA] Blueprint '{bp.name}' ya fue registrado, se omite duplicado."
            )
        else:
            app.register_blueprint(bp, url_prefix=prefix)
            registered_blueprints.add(bp.name)
            print(f"[OK] Registrado blueprint: {bp.name}")

    # Registrar blueprints
    from app.api.auth import auth_bp

    safe_register(auth_bp, "/auth")

    from app.api.qrs import qrs_bp

    safe_register(qrs_bp, "/qrs")

    from app.api.home import home_bp

    safe_register(home_bp, "/")

    from app.api.usuarios import usuario_bp

    safe_register(usuario_bp, "/usuarios")

    from app.api.eventos import evento_bp

    safe_register(evento_bp, "/eventos")

    from app.api.cursos import curso_bp

    safe_register(curso_bp, "/cursos")

    from app.api.inscripciones import ins_bp

    safe_register(ins_bp, "/ins")

    from app.api.notas import notas_bp

    safe_register(notas_bp, "/notas")

    from app.api.certificate import certificate_bp

    safe_register(certificate_bp, "/cert")

    from app.api.rxls import rxls_bp

    safe_register(rxls_bp, "/rxls")

    from app.api.qrscan import qrscan_bp

    safe_register(qrscan_bp, "/scan")

    from app.api.coordinador import coordinador_bp

    safe_register(coordinador_bp, "/coordinador")

    from app.api.ponente import ponente_bp

    safe_register(ponente_bp, "/ponente")

    # Configurar Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # --- Medición de tiempos de cada request ---
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        total_time = time.time() - g.start_time
        if not request.path.startswith("/static"):
            app.logger.info(f"{request.method} {request.path} {total_time:.4f}s")
        return response

    # --- Listar rutas registradas (solo una vez) ---
    print("\n[RUTAS REGISTRADAS EN FLASK]:")
    for rule in app.url_map.iter_rules():
        print(rule)

    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S"
    )
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return app
