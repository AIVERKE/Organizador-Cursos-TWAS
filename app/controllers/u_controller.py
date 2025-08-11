import psycopg2
from app.db_c import get_connection
from werkzeug.security import generate_password_hash


# --- Usuarios General
def obtener_usuarios(rol):
    conn = get_connection()  # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM Usuarios WHERE id_rol = %s", (rol,)
    )  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función


def obtener_usuarios_id(rol, id):
    conn = get_connection()  # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM Usuarios WHERE id_rol = %s and id_usuario=%s", (rol, id)
    )  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función


# --- Usuarios Estudiantes
def obtener_estudiantes():
    conn = get_connection()  # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM Usuarios WHERE id_rol = 3 ORDER BY id_usuario ASC;")  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función


def obtener_estudiante(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = %s ORDER BY id_usuario ASC;", (id_usuario,))
    row = cursor.fetchone()
    conn.close()
    return row


def actualizar_estudiante(
    id_usuario, nombre, apellido, email, contrasena, documento, pais_origen, id_rol
):
    query = """
        UPDATE Usuarios
        SET nombre = %s, apellido = %s, email = %s,
            documento = %s, pais_origen = %s, id_rol = %s
        WHERE id_usuario = %s
    """
    values = [nombre, apellido, email, documento, pais_origen, id_rol, id_usuario]

    if contrasena and contrasena.strip() != "":
        query = """
            UPDATE Usuarios
            SET nombre = %s, apellido = %s, email = %s,
                contrasena = %s, documento = %s, pais_origen = %s, id_rol = %s
            WHERE id_usuario = %s
        """
        hashed = generate_password_hash(contrasena)
        values = [
            nombre,
            apellido,
            email,
            hashed,
            documento,
            pais_origen,
            id_rol,
            id_usuario,
        ]
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(query, values)
    conn.commit()
    conn.close()


def crear_estudiante(nombre, apellido, email, contrasena, documento, pais_origen):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    id_rol = 3  # Por defecto: estudiante
    hashed = generate_password_hash(contrasena)
    cursor.execute(
        "INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (nombre, apellido, email, hashed, documento, pais_origen, id_rol),
    )
    conn.commit()
    conn.close()


def crear_estudiantes_bulk(lista_estudiantes):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 3  # Por defecto: estudiante
        for estudiante in lista_estudiantes:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    estudiante["nombre"],
                    estudiante["apellido"],
                    estudiante["email"],
                    estudiante["contrasena"],
                    estudiante["documento"],
                    estudiante["pais_origen"],
                    id_rol,
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

#----------------
import unicodedata
import re

def generar_contrasena(apellido, documento):
    # Elimina acentos y caracteres especiales
    apellido_normalizado = unicodedata.normalize('NFKD', apellido)
    apellido_sin_tildes = ''.join([c for c in apellido_normalizado if not unicodedata.combining(c)])
    apellido_limpio = re.sub(r'[^A-Za-z]', '', apellido_sin_tildes).lower()  # solo letras// ñ -> n
    primeros_digitos = str(documento)
    # return apellido_limpio + primeros_digitos[:3] #primeros 3 digidtos
    return apellido_limpio + primeros_digitos

def crear_estudiantes_con_inscripcion(lista_estudiantes):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 3  # Estudiante

        for est in lista_estudiantes:
            # 1) Buscar id_curso por nombre (case‐insensitive)
            cursor.execute(
                "SELECT id_curso FROM cursos WHERE LOWER(nombre) = LOWER(%s)",
                (est.get("nombre_curso","").strip(),)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Curso '{est.get('nombre_curso')}' no encontrado.")
            id_curso = row[0]

            # Automatizacion contrasena
            contrasena_auto = generar_contrasena(est["apellido"], est["documento"])
            hashed = generate_password_hash(contrasena_auto)
            # 2) Insertar usuario y obtener id_usuario
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_usuario
                """,
                (
                    est["nombre"], est["apellido"], est["email"],
                    hashed, est["documento"],
                    est["pais_origen"], id_rol
                )
            )
            id_usuario = cursor.fetchone()[0]

            # 3) Crear inscripción
            cursor.execute(
                "INSERT INTO inscripciones (id_usuario, id_curso, fecha_inscripcion) VALUES (%s,%s,CURRENT_DATE) RETURNING id_inscripcion",
                (id_usuario, id_curso)
            )
            id_insc = cursor.fetchone()[0]

            # 4) Crear nota inicial
            cursor.execute(
                "INSERT INTO notas (id_inscripcion, nota_final) VALUES (%s, %s)",
                (id_insc, 0.00)
            )

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()



def eliminar_estudiante(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("DELETE FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}

# ------------------------
# def obtener_materias_estudiante(id_usuario):
#     conn = get_connection()
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     # Trae id_inscripcion, id_curso, nombre de curso y nota_final (si existe)
#     cursor.execute("""
#         SELECT i.id_inscripcion,
#                c.id_curso,
#                c.nombre AS nombre_curso,
#                n.nota_final
#         FROM inscripciones i
#         JOIN cursos c USING(id_curso)
#         LEFT JOIN notas n USING(id_inscripcion)
#         WHERE i.id_usuario = %s;
#     """, (id_usuario,))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows


def obtener_materias_estudiante(id_usuario,cursor):
    cursor.execute("""
        SELECT i.id_inscripcion,
               c.id_curso,
               c.nombre AS nombre_curso,
               n.nota_final,
               n.id_nota
        FROM inscripciones i
        JOIN cursos c USING(id_curso)
        LEFT JOIN notas n USING(id_inscripcion)
        WHERE i.id_usuario = %s;
    """, (id_usuario,))
    return cursor.fetchall()

 


# def obtener_cursos_disponibles(id_usuario):
#     conn = get_connection()
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cursor.execute("""
#         SELECT id_curso, nombre
#         FROM cursos
#         WHERE id_curso NOT IN (
#             SELECT id_curso FROM inscripciones WHERE id_usuario = %s
#         )
#         ORDER BY nombre;
#     """, (id_usuario,))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows


def obtener_cursos_disponibles(id_usuario,cursor):
    cursor.execute("""
        SELECT id_curso, nombre
        FROM cursos
        WHERE id_curso NOT IN (
            SELECT id_curso FROM inscripciones WHERE id_usuario = %s
        )
        ORDER BY nombre;
    """, (id_usuario,))
    return cursor.fetchall()
    
def crear_inscripcion(id_usuario, id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inscripciones (id_usuario, id_curso, fecha_inscripcion) VALUES (%s,%s,CURRENT_DATE) RETURNING id_inscripcion",
        (id_usuario, id_curso)
    )
    id_insc = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO notas (id_inscripcion, nota_final) VALUES (%s, %s)",
        (id_insc, 0.00)
    )
    conn.commit()
    conn.close()

def eliminar_inscripcion(id_inscripcion,id_nota):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notas WHERE id_inscripcion = %s AND id_nota = %s", (id_inscripcion,id_nota))
    cursor.execute("DELETE FROM inscripciones WHERE id_inscripcion = %s", (id_inscripcion,))
    conn.commit()
    conn.close()


#--------------
# --- Usuarios Expositor


def actualizar_ponente(
    id_usuario, nombre, apellido, email, contrasena, documento, pais_origen, id_rol
):
    query = """
        UPDATE Usuarios
        SET nombre = %s, apellido = %s, email = %s,
            documento = %s, pais_origen = %s, id_rol = %s
        WHERE id_usuario = %s
    """
    values = [nombre, apellido, email, documento, pais_origen, id_rol, id_usuario]

    if contrasena and contrasena.strip() != "":
        query = """
            UPDATE Usuarios
            SET nombre = %s, apellido = %s, email = %s,
                contrasena = %s, documento = %s, pais_origen = %s, id_rol = %s
            WHERE id_usuario = %s
        """
        hashed = generate_password_hash(contrasena)
        values = [
            nombre,
            apellido,
            email,
            hashed,
            documento,
            pais_origen,
            id_rol,
            id_usuario,
        ]
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(query, values)
    conn.commit()
    conn.close()


def crear_ponente(nombre, apellido, email, contrasena, documento, pais_origen):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    id_rol = 2  # Por defecto: ponente
    hashed = generate_password_hash(contrasena)
    cursor.execute(
        "INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (nombre, apellido, email, hashed, documento, pais_origen, id_rol),
    )
    conn.commit()
    conn.close()


def crear_ponentes_bulk(lista_expositores):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 2  # Por defecto: ponentes
        for expositor in lista_expositores:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (
                    expositor["nombre"],
                    expositor["apellido"],
                    expositor["email"],
                    expositor["contrasena"],
                    expositor["documento"],
                    expositor["pais_origen"],
                    id_rol,
                ),
            )
        conn.commit()
    except Exception as e:
        print("Error al crear ponentes:", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def crear_ponentes_con_lote(lista_ponentes):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 2  # Ponente

        for p in lista_ponentes:
            # 1) Generar y hashear contraseña
            contrasena_auto = generar_contrasena(p["apellido"], p["documento"])
            hashed = generate_password_hash(contrasena_auto)

            # 2) Insertar usuario
            cursor.execute(
                """
                INSERT INTO usuarios (
                  nombre, apellido, email, contrasena, documento, pais_origen, id_rol
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_usuario
                """,
                (
                    p["nombre"],
                    p["apellido"],
                    p["email"],
                    hashed,
                    p["documento"],
                    p["pais_origen"],
                    id_rol
                )
            )
            # Opcional: recoger id_usuario si necesitas usarlo
            _ = cursor.fetchone()[0]

        conn.commit()

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()

def eliminar_ponente(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("DELETE FROM Usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


# ------------------------

# Cursos dictados por el ponente
def get_cursos_ponente(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id_curso, c.nombre, c.descripcion
        FROM cursos c
        WHERE c.id_ponente = %s
    """, (id_usuario,))
    cursos = cursor.fetchall()
    result = [{'id_curso': c[0], 'nombre': c[1], 'descripcion': c[2]} for c in cursos]
    cursor.close()
    conn.close()
    return (result)

# Cursos disponibles (sin ponente)
def get_cursos_disponibles_para_ponente():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_curso, nombre, descripcion
        FROM cursos
        WHERE id_ponente = 1
    """)
    cursos = cursor.fetchall()
    result = [{'id_curso': c[0], 'nombre': c[1], 'descripcion': c[2]} for c in cursos]
    cursor.close()
    conn.close()
    return (result)

# Asignar curso a ponente
def asignar_curso_a_ponente(id_usuario, id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cursos SET id_ponente = %s WHERE id_curso = %s
    """, (id_usuario, id_curso))
    conn.commit()
    cursor.close()
    conn.close()

# Quitar curso al ponente
def quitar_curso_a_ponente(id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cursos SET id_ponente = 1 WHERE id_curso = %s
    """, (id_curso,))
    conn.commit()
    cursor.close()
    conn.close()

# ------------------------