from app import db
from sqlalchemy import text
MENSAJE_DOCENTE="""
Por su colaboración como ponente en el tema  “XXX”.
Realizado en la ciudad La Paz del 11 al 15 de Marzo del 2024, auspiciado y organizado por la red internacional TYAN-TWAS y la Universidad Mayor de San Andrés.
"""
MENSAJE_APROBACION="""
Ha completado exitosamente el curso de “XXX” dictado por XXX, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés.
Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024', con una duración de 30 hrs. académicas equivalente a 1 CLAR (Crédito Latinoamericano de Referencia).
"""
MENSAJE_PARTICIPACION="""
Ha participado del curso de “XXX” dictado por XXX, inaugurado dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés.
Realizado en la ciudad La Paz del '11 al 15 de Marzo del 2024'.
"""
MENSAJE_COLABORACION="""
Ha coordinado y colaborado en el curso de ”XXX", inaugurada dentro del postgrado de Ciencias Químicas de la Facultad de Ciencias Puras y Naturales, de la Universidad Mayor de San Andrés. 
El evento se llevó a cabo en la ciudad de La Paz del 11 al 15 de marzo de 2024
"""



def get_inscripciones(id_usuario):
    with db.engine.connect() as conn:
        query = text(
            """
            SELECT c.nombre as nombre_curso 
            FROM inscripciones i
            JOIN cursos c ON i.id_curso = c.id_curso
            WHERE id_usuario = :id_usuario
            """
        )
        resultado = conn.execute(query, {"id_usuario": id_usuario}).fetchall()
    return resultado    

def get_cursos(id_usuario):
    with db.engine.connect() as conn:
        query = text(
            """
            SELECT c.nombre as nombre_curso, c.id_curso 
            FROM usuarios u 
            JOIN cursos c ON u.id_usuario = c.id_ponente
            WHERE id_usuario = :id_usuario;
            """ 
        )
        resultado = conn.execute(query, {"id_usuario": id_usuario}).fetchall()
    return resultado

import re
import unicodedata

def sanitize_filename(name: str) -> str:
    # 1. Normalizar y separar acentos
    normalized_name = unicodedata.normalize('NFD', name)
    
    # 2. Eliminar acentos y diacríticos (Convierte á en a, ñ en n)
    ascii_name = ''.join(c for c in normalized_name if unicodedata.category(c) != 'Mn')
    
    # 3. Eliminar caracteres que aún no sean ASCII (como los corruptos Ý y ¾)
    # y convertir a ASCII puro, eliminando cualquier cosa que no encaje.
    final_name = ascii_name.encode('ascii', 'ignore').decode('ascii')
    
    # 4. Reemplazar caracteres no seguros y espacios (incluido el \xa0 convertido en espacio)
    return re.sub(r'[<>:"/\\|?*\s]+', '_', final_name.strip())