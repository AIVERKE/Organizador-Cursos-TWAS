import psycopg2
from app.db_c import get_connection
from datetime import date

def obtener_cursos_full():
    conn = get_connection() 
    cursor = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor

    )
    # cursor.execute(
    #     """SELECT c.*,v.*,u.nombre as NombreU, u.apellido as ApellidoU 
    #     FROM cursos c JOIN usuarios u ON c.id_ponente = u.id_usuario
    #     JOIN version_evento v ON c.id_version = v.id_version
    #     """
    # )  
    cursor.execute("""
        SELECT 
            c.*, 
            v.*, 
            u.nombre as NombreU, 
            u.apellido as ApellidoU,
            ca.codigo AS pin_hoy
        FROM cursos c
        JOIN usuarios u ON c.id_ponente = u.id_usuario
        JOIN version_evento v ON c.id_version = v.id_version
        LEFT JOIN codigos_asistencia ca 
            ON ca.id_curso = c.id_curso AND ca.fecha_cr::date = %s
        ORDER BY c.id_curso
    """, (date.today(),))


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
        cursor.execute(
            """SELECT c.*,v.*,u.nombre as NombreU, u.apellido as ApellidoU 
        FROM cursos c JOIN usuarios u ON c.id_ponente = u.id_usuario
        JOIN version_evento v ON c.id_version = v.id_version
        WHERE id_curso = %s
        """,
            (id_curso,),
        )  # consulta SQL directa
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
                    1,  # por defecto 1 = sin ponente
                ),
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
                cursor.execute(
                    "DELETE FROM inscripciones WHERE id_curso = %s", (id_curso,)
                )
                cursor.execute("DELETE FROM cursos WHERE id_curso = %s", (id_curso,))
                conn.commit()
    except psycopg2.Error as e:
        print(f"[ERROR] eliminar_curso: {e}")
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


def obtener_cursos_disponibles(id_usuario):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        SELECT id_curso, nombre
        FROM cursos
        WHERE id_curso NOT IN (
            SELECT id_curso FROM inscripciones WHERE id_usuario = %s
        )
        ORDER BY nombre;
    """,
        (id_usuario,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# -------------------
def obtener_ponente_de_curso(id_curso):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT u.id_usuario,  u.apellido||' '||u.nombre
        FROM cursos c
        JOIN usuarios u ON c.id_ponente = u.id_usuario
        WHERE c.id_curso = %s
    """,
        (id_curso,),
    )
    ponentes = cur.fetchall()
    return [{"id": p[0], "nombre": p[1]} for p in ponentes]


def obtener_ponentes_disponibles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id_usuario, apellido || ' ' || nombre FROM usuarios
        WHERE id_rol = 2 AND id_usuario != 1
    """
    )
    ponentes = cur.fetchall()
    return [{"id": p[0], "nombre": p[1]} for p in ponentes]


def asignar_ponente(id_curso, id_ponente):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE cursos SET id_ponente = %s WHERE id_curso = %s
    """,
        (id_ponente, id_curso),
    )
    conn.commit()


def obtener_estudiantes_y_docente(id_curso):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
        SELECT 
            -- Datos del curso
            c.id_curso, c.nombre AS nombre_curso, c.descripcion, c.modalidad,
            
            -- Datos del docente
            d.id_usuario AS id_docente, d.nombre AS nombre_docente, d.apellido AS apellido_docente,
            
            -- Datos de los estudiantes
            e.id_usuario AS id_estudiante, e.nombre AS nombre_estudiante, 
            e.apellido AS apellido_estudiante, e.email
            
        FROM cursos c
        -- Relación con docente
        JOIN usuarios d ON c.id_ponente = d.id_usuario
        
        -- Relación con inscripciones
        JOIN inscripciones i ON c.id_curso = i.id_curso
        
        -- Relación con estudiantes
        JOIN usuarios e ON i.id_usuario = e.id_usuario
        
        WHERE c.id_curso = %s
          AND e.id_rol = (SELECT id_rol FROM roles WHERE nombre = 'Estudiante')
        ORDER BY e.apellido, e.nombre;
        """

        cursor.execute(query, (id_curso,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return None

        # Armamos el objeto estructurado
        curso_info = {
            "id_curso": rows[0]["id_curso"],
            "nombre": rows[0]["nombre_curso"],
            "descripcion": rows[0]["descripcion"],
            "modalidad": rows[0]["modalidad"],
            "docente": {
                "id_docente": rows[0]["id_docente"],
                "nombre": rows[0]["nombre_docente"],
                "apellido": rows[0]["apellido_docente"],
            },
            "estudiantes": [],
        }

        for row in rows:
            estudiante = {
                "id_estudiante": row["id_estudiante"],
                "nombre": row["nombre_estudiante"],
                "apellido": row["apellido_estudiante"],
                "email": row["email"],
            }
            curso_info["estudiantes"].append(estudiante)

        return curso_info

    except psycopg2.Error as e:
        print(f"[ERROR] obtener_estudiantes_y_docente: {e}")
        return None


# -------------------

# --------Manejo de Pines
from werkzeug.security import generate_password_hash, check_password_hash

import random
import string

from datetime import datetime, timedelta


# Generar un PIN visible para el docente
def generar_pin():
    # PIN de 6 dígitos
    import random

    pin = str(random.randint(100000, 999999))
    # Hash para guardar en BD
    pin_hash = generate_password_hash(pin)
    creacion = datetime.utcnow()
    # Expiración de 5 minutos
    # expiracion = creacion + timedelta(minutes=30) # cooldown de 30 minutos
    expiracion = creacion.replace(hour=23, minute=59, second=59, microsecond=999999)
    return pin, pin_hash, creacion, expiracion


def actualizar_pin_curso(id_curso):
    pin, pin_h, cr, exp = generar_pin()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE cursos
                    SET pin = %s, hora_cr = %s , hora_exp = %s
                    WHERE id_curso = %s
                """,
                    (pin_h, cr, exp, id_curso),
                )
                cur.execute("""
                    INSERT INTO codigos_asistencia (id_curso, codigo, fecha_cr)
                    VALUES (%s, %s, %s)
                """, (id_curso, pin, cr))

            conn.commit()
        return pin, exp.strftime("%Y-%m-%d %H:%M %S UTC")
    except psycopg2.Error as e:
        print(f"[ERROR] actualizar_pin_curso: {e}")
        return None, None


def verificar_pin(id_curso, pin_ingresado, hora_actual):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT  id_curso, pin,hora_cr,hora_exp FROM cursos
                    WHERE id_curso = %s 
                """,
                    (id_curso,),
                )
                curs = cur.fetchone()
                if not curs:
                    return False, "Curso no encontrado", "Course not founded"
                id_curso = curs[0]
                pin_hash = curs[1]
                hora_cr = curs[2]
                hora_exp = curs[3]
                if hora_actual > hora_exp:
                    return (
                        False,
                        "El Código de Asistencia ha expirado",
                        "The Attendance Code has expired",
                    )

                # Validar PIN ingresado
                if not check_password_hash(pin_hash, str(pin_ingresado)):
                    return (
                        False,
                        "Código de Asistencia incorrecto",
                        " Attendance Code Incorrect",
                    )

                return (
                    True,
                    "Su asistencia ha sido registrada Correctamente",
                    "Your attendance has been recorded correctly",
                )
    except psycopg2.Error as e:
        return False, "Error", "Error"


# --------------------

# grafica
def generar_graf_barra():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT split_part(c.nombre, ' ', 1) as nombre, COUNT(i.id_inscripcion) AS inscritos
                    FROM cursos c
                    LEFT JOIN inscripciones i ON c.id_curso = i.id_curso
                    GROUP BY c.id_curso
                    ORDER BY inscritos DESC
                """)
                rows = cur.fetchall()
        data = [{"nombre": r[0], "inscritos": r[1]} for r in rows]
        return True,data
    except psycopg2.Error as e:
        return  False, str(e)