from app.extensions import db

class Rol(db.Model):
    __tablename__ = 'roles'  
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    # Relación inversa si quieres acceder a los usuarios desde rol
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)
