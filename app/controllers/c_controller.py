import psycopg2
from app.db_c import get_connection


def obtener_cursos_full():
    conn = get_connection()  # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # crea un cursor (como el "puente" para hacer consultas)
    cursor.execute("""SELECT c.*,v.*,u.nombre as NombreU, u.apellido as ApellidoU 
        FROM cursos c JOIN usuarios u ON c.id_ponente = u.id_usuario
        JOIN version_evento v ON c.id_version = v.id_version
        """)  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función

def obtener_cursos():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM cursos")
                return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"[ERROR] obtener_cursos: {e}")
        return []

def obtener_curso_id(id_curso):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""SELECT c.*,v.*,u.nombre as NombreU, u.apellido as ApellidoU 
        FROM cursos c JOIN usuarios u ON c.id_ponente = u.id_usuario
        JOIN version_evento v ON c.id_version = v.id_version
        WHERE id_curso = %s
        """,(id_curso,))  # consulta SQL directa
        row = cursor.fetchall()
        conn.close()
        return row
    except psycopg2.Error as e:
        print(f"[ERROR] obtener_curso: {e}")
        return None


def crear_curso(nombre, descripcion, modalidad, id_version, id_ponente):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO cursos (nombre, descripcion, modalidad, id_version, id_ponente)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (nombre, descripcion, modalidad, id_version, id_ponente),
                )
                conn.commit()
    except psycopg2.Error as e:
        print(f"[ERROR] crear_curso: {e}")

import psycopg2
from app.db_c import get_connection

def crear_cursos_con_lote(lista_cursos):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for c in lista_cursos:
            cursor.execute(
                """
                INSERT INTO cursos (nombre, descripcion, modalidad, id_version, id_ponente)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    c["nombre"].strip(),
                    c["descripcion"].strip(),
                    c["modalidad"].strip(),
                    1,
                    1  # por defecto 1 = sin ponente
                )
            )
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        # Aquí podrías loguear e informar el error
        raise
    finally:
        if conn:
            conn.close()

def actualizar_curso_base(id_curso, nombre, descripcion, modalidad):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE cursos
                    SET nombre = %s, descripcion = %s, modalidad = %s
                    WHERE id_curso = %s
                    """,
                    (nombre, descripcion, modalidad, id_curso),
                )
                conn.commit()
    except psycopg2.Error as e:
        print(f"[ERROR] actualizar_curso: {e}")

def actualizar_curso(id_curso, nombre, descripcion, modalidad, id_version, id_ponente):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE cursos
                    SET nombre = %s, descripcion = %s, modalidad = %s, id_version = %s, id_ponente = %s
                    WHERE id_curso = %s
                    """,
                    (nombre, descripcion, modalidad, id_version, id_ponente, id_curso),
                )
                conn.commit()
    except psycopg2.Error as e:
        print(f"[ERROR] actualizar_curso: {e}")        

def eliminar_curso(id_curso):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM inscripciones WHERE id_curso = %s", (id_curso,))
                cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (id_curso,))
                conn.commit()
    except psycopg2.Error as e:
        print(f"[ERROR] eliminar_curso: {e}")
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}

def obtener_cursos_disponibles(id_usuario):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT id_curso, nombre
        FROM cursos
        WHERE id_curso NOT IN (
            SELECT id_curso FROM inscripciones WHERE id_usuario = %s
        )
        ORDER BY nombre;
    """, (id_usuario,))
    rows = cursor.fetchall()
    conn.close()
    return rows

#-------------------
def obtener_ponente_de_curso(id_curso):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id_usuario,  u.apellido||' '||u.nombre
        FROM cursos c
        JOIN usuarios u ON c.id_ponente = u.id_usuario
        WHERE c.id_curso = %s
    """,(id_curso,))
    ponentes = cur.fetchall()
    return [{"id": p[0], "nombre": p[1]} for p in ponentes]

def obtener_ponentes_disponibles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_usuario, apellido || ' ' || nombre FROM usuarios
        WHERE id_rol = 2 AND id_usuario != 1
    """)
    ponentes = cur.fetchall()
    return [{"id": p[0], "nombre": p[1]} for p in ponentes]

def asignar_ponente(id_curso, id_ponente):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE cursos SET id_ponente = %s WHERE id_curso = %s
    """, (id_ponente, id_curso))
    conn.commit()

#-------------------