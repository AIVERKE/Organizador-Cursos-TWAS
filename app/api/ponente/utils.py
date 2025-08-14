import psycopg2.extras
from app.api.ponente.db_helper import nueva_conexion

def obtener_estudiantes_inscritos(id_curso):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY u.apellido) AS numero,
                u.apellido, 
                u.nombre,
                u.pais_origen, 
                u.email
            FROM usuarios u
            JOIN inscripciones i ON u.id_usuario = i.id_usuario
            JOIN cursos c ON i.id_curso = c.id_curso AND c.id_curso = %s
            JOIN version_evento v ON c.id_version = v.id_version AND v.anio = EXTRACT(YEAR FROM CURRENT_DATE)
            WHERE u.id_rol = 3
            ORDER BY u.apellido;
        """
        cursor.execute(query, (id_curso,))
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()

def obtener_estudiantes_inscritos_nota(id_curso):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY u.apellido) AS nro,
                i.id_inscripcion,
                u.nombre,
                u.apellido,
                COUNT(a.presente) AS total_asistencias,
                n.nota_final
            FROM inscripciones i
            JOIN usuarios u ON i.id_usuario = u.id_usuario
            LEFT JOIN asistencias a 
                ON a.id_inscripcion = i.id_inscripcion 
                AND EXTRACT(YEAR FROM a.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND a.presente = TRUE
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            WHERE i.id_curso = %s
            GROUP BY u.id_usuario, u.nombre, u.apellido, n.nota_final, i.id_inscripcion
            ORDER BY u.apellido;
        """
        cursor.execute(query, (id_curso,))
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()

def obtener_id_curso(id_usuario):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT c.id_curso
            FROM cursos c
            JOIN version_evento v ON c.id_version = v.id_version
            WHERE c.id_ponente = %s AND v.anio = EXTRACT(YEAR FROM CURRENT_DATE)
            LIMIT 1;
        """
        cursor.execute(query, (id_usuario,))
        result = cursor.fetchone()
        if result:
            return result["id_curso"]
        else:
            return None
    finally:
        conn.close()
#--------------------------------------------------------------------------------------------
def actualizar_nota_final(id_inscripcion, nota_final):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notas SET nota_final = %s WHERE id_inscripcion = %s
        """, (nota_final, id_inscripcion))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def actualizar_nota_asistencia(id_inscripcion, nota_asistencia):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notas SET nota_asistencia = %s WHERE id_inscripcion = %s
        """, (nota_asistencia, id_inscripcion))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def actualizar_nota_acumulada(id_inscripcion, nota_acumulada):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notas SET nota_acumulada = %s WHERE id_inscripcion = %s
        """, (nota_acumulada, id_inscripcion))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
#-----------------------------------------------------

def obtener_nombre_curso(id_usuario):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT c.nombre, c.descripcion
            FROM cursos c
            JOIN version_evento v ON c.id_version = v.id_version
            WHERE c.id_ponente = %s AND v.anio = EXTRACT(YEAR FROM CURRENT_DATE)
            LIMIT 1;
        """
        cursor.execute(query, (id_usuario,))
        result = cursor.fetchone()
        if result:
            return result["nombre"], result["descripcion"]
        else:
            return None
    finally:
        conn.close()       