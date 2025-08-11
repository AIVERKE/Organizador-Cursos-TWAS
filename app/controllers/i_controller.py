import psycopg2

import psycopg2.extras

from app.db_c import get_connection


def obtener_inscripciones():
    conn = get_connection()  # conecta a la base de datos
    cursor = conn.cursor()  # crea un cursor (como el "puente" para hacer consultas)
    cursor.execute("SELECT * FROM inscripciones")  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función


def obtener_inscripcion(id_inscripcion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM inscripciones WHERE id_inscripcion= %s", (id_inscripcion,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def crear_inscripcion(id_usuario, id_curso, fecha_inscripcion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inscripciones (id_usuario, id_curso, fecha_inscripcion) VALUES (%s,%s,%s)",
        (
            id_usuario,
            id_curso,
            fecha_inscripcion,
        ),
    )
    conn.commit()
    conn.close()


def actualizar_inscripcion(id_inscripcion, id_usuario, id_curso, fecha_inscripcion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE inscripciones SET id_usuario = %s, id_curso = %s, fecha_inscripcion = %s WHERE id_inscripcion = %s",
        (id_usuario, id_curso, fecha_inscripcion, id_inscripcion),
    )
    conn.commit()
    conn.close()


def eliminar_inscripcion(id_inscripcion):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM inscripciones WHERE id_inscripcion = %s", (id_inscripcion,)
        )
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


# funcion agregada 31-07-2025 9:52 pm para el funcionamiento de la vista cursos en el frontend.
def obtener_inscripciones_por_usuario(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT i.id_inscripcion, c.id_curso, c.nombre, c.descripcion, c.modalidad, ve.nombre_version, ve.anio
        FROM inscripciones i
        JOIN cursos c ON i.id_curso = c.id_curso
        JOIN version_evento ve ON c.id_version = ve.id_version
        WHERE i.id_usuario = %s
    """,
        (id_usuario,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def obtener_inscripciones_usuario(id_usuario):
    try:
        print(" Inicio de función obtener_inscripciones_usuario")
        conn = get_connection()
        print(" Conexión obtenida")

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        print(" Cursor creado")

        cursor.execute(
            """
            SELECT i.id_inscripcion, c.id_curso, c.nombre, c.descripcion, 
                   c.modalidad, ve.nombre_version, ve.anio
            FROM inscripciones i
            JOIN cursos c ON i.id_curso = c.id_curso
            JOIN version_evento ve ON c.id_version = ve.id_version
            WHERE i.id_usuario = %s
            """,
            (id_usuario,),
        )
        print(" Consulta ejecutada")

        rows = cursor.fetchall()
        print(f" {len(rows)} filas recuperadas")

        cursor.close()
        print(" Cursor cerrado")

        return rows

    except Exception as e:
        print(" Error en obtener_inscripciones_usuario:", str(e))
        return None
