import psycopg2
import psycopg2.extras
from app.db_c import get_connection

def crear_nota(id_inscripcion, nota_final, nota_asistencia, nota_acumulada):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO notas (id_inscripcion, nota_final, nota_asistencia, nota_acumulada)
        VALUES (%s, %s, %s, %s)
        """,
        (id_inscripcion, nota_final, nota_asistencia, nota_acumulada),
    )
    conn.commit()
    conn.close()

def obtener_notas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas")
    rows = cursor.fetchall()
    conn.close()
    return rows


def obtener_nota(id_nota):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM notas WHERE id_nota = %s", (id_nota,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def actualizar_nota(id_nota, id_inscripcion, nota_final, nota_asistencia, nota_acumulada):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE notas
        SET id_inscripcion = %s,
            nota_final = %s,
            nota_asistencia = %s,
            nota_acumulada = %s
        WHERE id_nota = %s
        """,
        (id_inscripcion, nota_final, nota_asistencia, nota_acumulada, id_nota),
    )
    conn.commit()
    conn.close()


def eliminar_nota(id_nota):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM notas WHERE id_nota = %s", (id_nota,)
        )
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


def obtener_notas_por_inscripcion(id_inscripcion):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        SELECT n.id_nota, n.nota_final, n.nota_asistencia, n.nota_acumulada,
               i.id_usuario, c.nombre AS nombre_curso
        FROM notas n
        JOIN inscripciones i ON n.id_inscripcion = i.id_inscripcion
        JOIN cursos c ON i.id_curso = c.id_curso
        WHERE n.id_inscripcion = %s
        """,
        (id_inscripcion,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
