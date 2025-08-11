from app.extensions import db
from flask_login import UserMixin


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(200), nullable=False)
    documento = db.Column(db.String(30), nullable=False)
    pais_origen = db.Column(db.String(50), nullable=False)

    # Clave foránea
    id_rol = db.Column(db.Integer, db.ForeignKey("roles.id_rol"))

    def get_id(self):
        return str(self.id_usuario)
