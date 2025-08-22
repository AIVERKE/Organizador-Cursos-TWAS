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
                n.nota_final,
                n.nota_asistencia,
                n.nota_acumulada
            FROM inscripciones i
            JOIN usuarios u ON i.id_usuario = u.id_usuario
            LEFT JOIN asistencias a 
                ON a.id_inscripcion = i.id_inscripcion 
                AND EXTRACT(YEAR FROM a.fecha) = EXTRACT(YEAR FROM CURRENT_DATE)
                AND a.presente = TRUE
            LEFT JOIN notas n ON n.id_inscripcion = i.id_inscripcion
            WHERE i.id_curso = %s
            GROUP BY 
                u.id_usuario, 
                u.nombre, 
                u.apellido, 
                n.nota_final, 
                n.nota_asistencia, 
                n.nota_acumulada, 
                i.id_inscripcion
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


# --------------------------------------------------------------------------------------------
def actualizar_nota_final(id_inscripcion, nota_final):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE notas SET nota_final = %s WHERE id_inscripcion = %s
        """,
            (nota_final, id_inscripcion),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def actualizar_nota_asistencia(id_inscripcion, nota_asistencia):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notas SET nota_asistencia = %s WHERE id_inscripcion = %s",
            (nota_asistencia, id_inscripcion),
        )
        conn.commit()
        # Recalcular la nota final
        recalcular_nota_final(id_inscripcion)
    finally:
        cursor.close()
        conn.close()


def actualizar_nota_acumulada(id_inscripcion, nota_acumulada):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notas SET nota_acumulada = %s WHERE id_inscripcion = %s",
            (nota_acumulada, id_inscripcion),
        )
        conn.commit()
        # Recalcular la nota final
        recalcular_nota_final(id_inscripcion)
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------


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


# ----------------Calculo notas asistencia--------------------
def calcular_nota_asistencia(id_curso):
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Obtener todas las inscripciones del curso con su total de asistencias
        query_asistencias = """
            SELECT i.id_inscripcion, COUNT(a.id_asistencia) AS total_asistencias
            FROM inscripciones i
            LEFT JOIN asistencias a ON a.id_inscripcion = i.id_inscripcion
            WHERE i.id_curso = %s
            GROUP BY i.id_inscripcion;
        """
        cursor.execute(query_asistencias, (id_curso,))
        inscripciones = cursor.fetchall()

        # Para cada inscripción, calcular y actualizar la nota de asistencia
        for inscripcion in inscripciones:
            total_asistencias = inscripcion["total_asistencias"]

            if total_asistencias == 0:
                nota_asistencia = 0
            elif total_asistencias == 1:
                nota_asistencia = 1
            elif total_asistencias == 2:
                nota_asistencia = 2
            else:
                nota_asistencia = 5

            query_update = """
                UPDATE notas
                SET nota_asistencia = %s
                WHERE id_inscripcion = %s;
            """
            cursor.execute(
                query_update, (nota_asistencia, inscripcion["id_inscripcion"])
            )

        conn.commit()

    finally:
        conn.close()


def recalcular_nota_final(id_inscripcion):
    """
    Calcula la nota final como la suma de la nota acumulada y la nota de asistencia.
    """
    conn = nueva_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT nota_acumulada, nota_asistencia FROM notas WHERE id_inscripcion = %s",
            (id_inscripcion,),
        )
        notas = cursor.fetchone()
        if notas:
            nota_acumulada = notas["nota_acumulada"] or 0
            nota_asistencia = notas["nota_asistencia"] or 0
            nota_final = nota_acumulada + nota_asistencia
            # Actualizamos la nota final
            actualizar_nota_final(id_inscripcion, nota_final)
    finally:
        conn.close()
