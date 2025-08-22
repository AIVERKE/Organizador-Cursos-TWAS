import psycopg2
from app.db_c import get_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date

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
    cursor.execute(
        "SELECT * FROM Usuarios WHERE id_rol = 3 ORDER BY id_usuario ASC;"
    )  # consulta SQL directa
    rows = cursor.fetchall()  # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows  # devuelve los datos a quien haya llamado esta función


def obtener_estudiante(id_usuario):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Usuarios WHERE id_usuario = %s ORDER BY id_usuario ASC;",
        (id_usuario,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


# ----cambio 1
def actualizar_estudiante(id_usuario,nombre,apellido,email,contrasena,documento,pais_origen,id_rol,fecha_nac,genero,pais_residencia,afiliacion_u,tipo_afiliacion,area_tematica,disciplina_cientifica):
    query = """
        UPDATE public.usuarios
        SET nombre = %s,
            apellido = %s,
            email = %s,
            documento = %s,
            pais_origen = %s,
            id_rol = %s,
            fecha_nac = %s,
            genero = %s,
            pais_residencia = %s,
            afiliacion_u = %s,
            tipo_afiliacion = %s,
            area_tematica = %s,
            disciplina_cientifica = %s
        WHERE id_usuario = %s
    """
    values = [
        nombre,
        apellido,
        email,
        documento,
        pais_origen,
        id_rol,
        fecha_nac,
        genero,
        pais_residencia,
        afiliacion_u,
        tipo_afiliacion,
        area_tematica,
        disciplina_cientifica,
        id_usuario,
    ]

    # --- Rama con cambio de contraseña ---
    if contrasena and contrasena.strip():
        query = """
            UPDATE public.usuarios
            SET nombre = %s,
                apellido = %s,
                email = %s,
                contrasena = %s,
                documento = %s,
                pais_origen = %s,
                id_rol = %s,
                fecha_nac = %s,
                genero = %s,
                pais_residencia = %s,
                afiliacion_u = %s,
                tipo_afiliacion = %s,
                area_tematica = %s,
                disciplina_cientifica = %s
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
            fecha_nac,
            genero,
            pais_residencia,
            afiliacion_u,
            tipo_afiliacion,
            area_tematica,
            disciplina_cientifica,
            id_usuario,
        ]

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, values)
        conn.commit()
    finally:
        conn.close()


# ------------------------------Cambio2-----------------------------------------


def crear_estudiante(
    nombre,
    apellido,
    email,
    contrasena,
    documento,
    pais_origen,
    fecha_nac,
    genero,
    pais_residencia,
    afiliacion_u,
    tipo_afiliacion,
    area_tematica,
    disciplina_cientifica,
):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    id_rol = 3  # Por defecto: estudiante
    hashed = generate_password_hash(contrasena)
    cursor.execute(
        "INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            nombre,
            apellido,
            email,
            hashed,
            documento,
            pais_origen,
            id_rol,
            fecha_nac,
            genero,
            pais_residencia,
            afiliacion_u,
            tipo_afiliacion,
            area_tematica,
            disciplina_cientifica
        ),
    )
    conn.commit()
    conn.close()


# --------------------Cambio 3------------------------------
def crear_estudiantes_bulk(lista_estudiantes):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 3  # Por defecto: estudiante
        for estudiante in lista_estudiantes:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    estudiante["nombre"],
                    estudiante["apellido"],
                    estudiante["email"],
                    estudiante["contrasena"],
                    estudiante["documento"],
                    estudiante["pais_origen"],
                    id_rol,
                    estudiante["fecha_nac"],
                    estudiante["genero"],
                    estudiante["pais_residencia"],
                    estudiante["afiliacion_u"],
                    estudiante["tipo_afiliacion"],
                    estudiante["area_tematica"],
                    estudiante["disciplina_cientifica"],
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


# ---------------- cambiado hasta aqui por hoy ------------------
import unicodedata
import re


def generar_contrasena(apellido, documento):
    # Elimina acentos y caracteres especiales
    apellido_normalizado = unicodedata.normalize("NFKD", apellido)
    apellido_sin_tildes = "".join(
        [c for c in apellido_normalizado if not unicodedata.combining(c)]
    )
    apellido_limpio = re.sub(
        r"[^A-Za-z]", "", apellido_sin_tildes
    ).lower()  # solo letras// ñ -> n
    primeros_digitos = str(documento)
    # return apellido_limpio + primeros_digitos[:3] #primeros 3 digidtos
    return apellido_limpio + primeros_digitos


def crear_estudiantes_con_inscripcion_con_lote(lista_estudiantes):
    conn = None
    registrados = []
    fallidos = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 3

        for est in lista_estudiantes:
            try:

                # 1) Buscar id_curso por nombre (case‐insensitive)
                cursor.execute(
                    "SELECT id_curso FROM cursos WHERE LOWER(nombre) = LOWER(%s)",
                    (est.get("nombre_curso", "").strip(),),
                )
                row = cursor.fetchone()
                if not row:
                    fallidos.append({
                        "usuario": est,
                        "error": "Curso no encontrado"
                    })
                    continue    
                id_curso = row[0]

                # Automatizacion contrasena
                hashed = generate_password_hash(
                    generar_contrasena(est["apellido"], est["documento"])
                )
                # 2) Insertar usuario y obtener id_usuario
                cursor.execute(
                    """
                    INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id_usuario
                    """,
                    (
                        est["nombre"],
                        est["apellido"],
                        est["email"],
                        hashed,
                        est["documento"],
                        est["pais_origen"],
                        id_rol,
                        est["fecha_nac"],
                        est["genero"],
                        est["pais_residencia"],
                        est["afiliacion_u"],
                        est["tipo_afiliacion"],
                        est["area_tematica"],
                        est["disciplina_cientifica"],
                    ),
                )
                id_usuario = cursor.fetchone()[0]
                # 3) Crear inscripción
                cursor.execute(
                    """
                    INSERT INTO inscripciones (id_usuario,id_curso,fecha_inscripcion,modalidad,certificado_generado) 
                    VALUES (%s,%s,%s,%s,%s) RETURNING id_inscripcion
                    """,
                    (id_usuario, id_curso,date.today(),est["modalidad"],False),
                )
                id_insc = cursor.fetchone()[0]

                # 4) Crear nota inicial
                cursor.execute(
                    """INSERT INTO notas (id_inscripcion, nota_final, nota_asistencia, nota_acumulada) 
                    VALUES (%s, %s, %s,%s)
                    """,
                    (id_insc, 0.00, 0.00, 0.00),
                )
                
                registrados.append({
                    "usuario": est,
                    "id_usuario": id_usuario,
                    "id_inscripcion": id_insc
                })

            except Exception as e:
                conn.rollback()
                fallidos.append({
                        "usuario": est,
                        "error": str(e)
                })
                continue

        conn.commit()  # confirmo todo lo que sí funcionó
        return {"registrados": registrados, "fallidos": fallidos}
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
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


def obtener_materias_estudiante(id_usuario, cursor):
    cursor.execute(
        """
        SELECT i.id_inscripcion,
               c.id_curso,
               c.nombre AS nombre_curso,
               n.nota_final,
               n.id_nota
        FROM inscripciones i
        JOIN cursos c USING(id_curso)
        LEFT JOIN notas n USING(id_inscripcion)
        WHERE i.id_usuario = %s;
    """,
        (id_usuario,),
    )
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


def obtener_cursos_disponibles(id_usuario, cursor):
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
    return cursor.fetchall()


def crear_inscripcion(id_usuario, id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inscripciones (id_usuario, id_curso, fecha_inscripcion) VALUES (%s,%s,CURRENT_DATE) RETURNING id_inscripcion",
        (id_usuario, id_curso),
    )
    id_insc = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO notas (id_inscripcion, nota_final) VALUES (%s, %s)",
        (id_insc, 0.00),
    )
    conn.commit()
    conn.close()


def eliminar_inscripcion(id_inscripcion, id_nota):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM notas WHERE id_inscripcion = %s AND id_nota = %s",
        (id_inscripcion, id_nota),
    )
    cursor.execute(
        "DELETE FROM inscripciones WHERE id_inscripcion = %s", (id_inscripcion,)
    )
    conn.commit()
    conn.close()


# --------------
# --- Usuarios Expositor

'''
def actualizar_ponente(
    id_usuario, nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica
):
    query = """
        UPDATE Usuarios
        SET nombre = %s, apellido = %s, email = %s,
            documento = %s, pais_origen = %s, id_rol = %s
        WHERE id_usuario = %s
    """
    values = [nombre, apellido, email, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica, id_usuario]

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
            fecha_nac, 
            genero, 
            pais_residencia, 
            afiliacion_u, 
            tipo_afiliacion, 
            area_tematica, 
            disciplina_cientifica,
            id_usuario,
        ]
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(query, values)
    conn.commit()
    conn.close()
'''


def actualizar_ponente(
    id_usuario,
    nombre,
    apellido,
    email,
    contrasena,
    documento,
    pais_origen,
    id_rol,
    fecha_nac,
    genero,  # 'male' | 'female' | 'other'
    pais_residencia,
    afiliacion_u,
    tipo_afiliacion,  # 'public' | 'private'
    area_tematica,
    disciplina_cientifica,
):
    # --- Rama base: sin cambio de contraseña ---
    query = """
        UPDATE public.usuarios
        SET nombre = %s,
            apellido = %s,
            email = %s,
            documento = %s,
            pais_origen = %s,
            id_rol = %s,
            fecha_nac = %s,
            genero = %s,
            pais_residencia = %s,
            afiliacion_u = %s,
            tipo_afiliacion = %s,
            area_tematica = %s,
            disciplina_cientifica = %s
        WHERE id_usuario = %s
    """
    values = [
        nombre,
        apellido,
        email,
        documento,
        pais_origen,
        id_rol,
        fecha_nac,
        genero,
        pais_residencia,
        afiliacion_u,
        tipo_afiliacion,
        area_tematica,
        disciplina_cientifica,
        id_usuario,
    ]

    # --- Rama con cambio de contraseña ---
    if contrasena and contrasena.strip():
        hashed = generate_password_hash(contrasena)
        query = """
            UPDATE public.usuarios
            SET nombre = %s,
                apellido = %s,
                email = %s,
                contrasena = %s,
                documento = %s,
                pais_origen = %s,
                id_rol = %s,
                fecha_nac = %s,
                genero = %s,
                pais_residencia = %s,
                afiliacion_u = %s,
                tipo_afiliacion = %s,
                area_tematica = %s,
                disciplina_cientifica = %s
            WHERE id_usuario = %s
        """
        values = [
            nombre,
            apellido,
            email,
            hashed,
            documento,
            pais_origen,
            id_rol,
            fecha_nac,
            genero,
            pais_residencia,
            afiliacion_u,
            tipo_afiliacion,
            area_tematica,
            disciplina_cientifica,
            id_usuario,
        ]

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, values)
        conn.commit()
    finally:
        conn.close()


def crear_ponente(
    nombre,
    apellido,
    email,
    contrasena,
    documento,
    pais_origen,
    fecha_nac,
    genero,
    pais_residencia,
    afiliacion_u,
    tipo_afiliacion,
    area_tematica,
    disciplina_cientifica,
):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    id_rol = 2  # Por defecto: ponente
    hashed = generate_password_hash(contrasena)
    cursor.execute(
        "INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            nombre,
            apellido,
            email,
            hashed,
            documento,
            pais_origen,
            id_rol,
            fecha_nac,
            genero,
            pais_residencia,
            afiliacion_u,
            tipo_afiliacion,
            area_tematica,
            disciplina_cientifica,
        ),
    )
    conn.commit()
    conn.close()


# -----------------------------------
def crear_ponentes_bulk(lista_expositores):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 2  # Por defecto: ponentes
        for expositor in lista_expositores:
            cursor.execute(
                """
                INSERT INTO Usuarios (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    expositor["nombre"],
                    expositor["apellido"],
                    expositor["email"],
                    expositor["contrasena"],
                    expositor["documento"],
                    expositor["pais_origen"],
                    id_rol,
                    expositor["fecha_nac"],
                    expositor["genero"],
                    expositor["pais_residencia"],
                    expositor["afiliacion_u"],
                    expositor["tipo_afiliacion"],
                    expositor["area_tematica"],
                    expositor["disciplina_cientifica"],
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
    registrados = []
    fallidos = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 2

        for p in lista_ponentes:
            try:
                # 1) Generar y hashear contraseña
                hashed = generate_password_hash(
                    generar_contrasena(p["apellido"], p["documento"])
                )

                # 2) Insertar usuario
                cursor.execute(
                    """
                    INSERT INTO Usuarios 
                        (nombre, apellido, email, contrasena, documento, pais_origen, id_rol, 
                         fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, 
                         area_tematica, disciplina_cientifica)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_usuario
                    """,
                    (
                        p["nombre"],
                        p["apellido"],
                        p["email"],
                        hashed,
                        p["documento"],
                        p["pais_origen"],
                        id_rol,
                        p["fecha_nac"],
                        p["genero"],
                        p["pais_residencia"],
                        p["afiliacion_u"],
                        p["tipo_afiliacion"],
                        p["area_tematica"],
                        p["disciplina_cientifica"],
                    ),
                )
                # Opcional: recoger id_usuario si necesitas usarlo
                id_usuario  = cursor.fetchone()[0]

                registrados.append({
                    "usuario": p,
                    "id_usuario": id_usuario
                })
            except Exception as e:
                # Si falla un usuario, lo guardamos en fallidos con el error
                fallidos.append({
                    "usuario": p,
                    "error": str(e)
                })
                conn.rollback()  # rollback solo para esa query
                cursor = conn.cursor()  # reset cursor para continuar con el siguiente
            conn.commit()
            return {"registrados": registrados, "fallidos": fallidos}

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
    cursor.execute(
        """
        SELECT c.id_curso, c.nombre, c.descripcion
        FROM cursos c
        WHERE c.id_ponente = %s
    """,
        (id_usuario,),
    )
    cursos = cursor.fetchall()
    result = [{"id_curso": c[0], "nombre": c[1], "descripcion": c[2]} for c in cursos]
    cursor.close()
    conn.close()
    return result


# Cursos disponibles (sin ponente)
def get_cursos_disponibles_para_ponente():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id_curso, nombre, descripcion
        FROM cursos
        WHERE id_ponente = 1
    """
    )
    cursos = cursor.fetchall()
    result = [{"id_curso": c[0], "nombre": c[1], "descripcion": c[2]} for c in cursos]
    cursor.close()
    conn.close()
    return result


# Asignar curso a ponente
def asignar_curso_a_ponente(id_usuario, id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE cursos SET id_ponente = %s WHERE id_curso = %s
    """,
        (id_usuario, id_curso),
    )
    conn.commit()
    cursor.close()
    conn.close()


# Quitar curso al ponente
def quitar_curso_a_ponente(id_curso):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE cursos SET id_ponente = 1 WHERE id_curso = %s
    """,
        (id_curso,),
    )
    conn.commit()
    cursor.close()
    conn.close()


# ------------------------
