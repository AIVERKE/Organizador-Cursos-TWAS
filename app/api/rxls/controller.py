import psycopg2
from app.db_c import get_connection


def obtener_estudiantes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios")
    rows = cursor.fetchall()
    conn.close()
    return rows


def obtener_estudiante(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
    row = cursor.fetchone()
    conn.close()
    return row


def crear_estudiante(nombre, apellido, email, contrasena, documento, pais_origen):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (nombre, apellido, email, contrasena, documento, pais_origen),
        )
        conn.commit()
    except Exception as e:
        print("Error al crear estudiante:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def crear_estudiantes_bulk(lista_estudiantes):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for estudiante in lista_estudiantes:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    estudiante["nombre"],
                    estudiante["apellido"],
                    estudiante["email"],
                    estudiante["contrasena"],
                    estudiante["documento"],
                    estudiante["pais_origen"],
                ),
            )
        conn.commit()
    except Exception as e:
        print("Error al crear estudiantes:", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def actualizar_estudiante(
    id_usuario, nombre, apellido, email, contrasena, documento, pais_origen
):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Usuarios 
            SET nombre = %s, apellido = %s, email = %s, contrasena = %s, documento = %s, pais_origen = %s 
            WHERE id_usuario = %s
        """,
            (nombre, apellido, email, contrasena, documento, pais_origen, id_usuario),
        )
        conn.commit()
    except Exception as e:
        print("Error al actualizar estudiante:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def eliminar_estudiante(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}
    finally:
        if conn:
            conn.close()
