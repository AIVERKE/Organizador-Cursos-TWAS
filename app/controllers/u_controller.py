import psycopg2
from app.db_c import get_connection
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
from flask import jsonify
import pandas as pd

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


# def obtener_usuarios_id(rol, id):
#     conn = get_connection()  # conecta a la base de datos
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#     cursor.execute(
#         "SELECT * FROM Usuarios WHERE id_rol = %s and id_usuario=%s", (rol, id)
#     )  # consulta SQL directa
#     rows = cursor.fetchall()  # obtiene todos los resultados en una lista
#     conn.close()  # cierra la conexión
#     return rows  # devuelve los datos a quien haya llamado esta función

def obtener_usuarios_id(rol, id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM Usuarios WHERE id_rol = %s and id_usuario=%s", (rol, id))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        r = rows[0]
        fn = r.get("fecha_nac")
        # Convierte date/datetime a 'YYYY-MM-DD'
        if fn:
            try:
                r["fecha_nac"] = fn.isoformat()[:10]
            except Exception:
                r["fecha_nac"] = str(fn)[:10]
        return [r]
    return []



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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT * FROM Usuarios WHERE id_usuario = %s ORDER BY id_usuario ASC;",
        (id_usuario,),
    )
    row = cursor.fetchone()
    conn.close()
    return row or {}


# ----cambio 1
# def actualizar_estudiante(id_usuario,nombre,apellido,email,contrasena,documento,pais_origen,id_rol,fecha_nac,genero,pais_residencia,afiliacion_u,tipo_afiliacion,area_tematica,disciplina_cientifica):
#     query = """
#         UPDATE public.usuarios
#         SET nombre = %s,
#             apellido = %s,
#             email = %s,
#             documento = %s,
#             pais_origen = %s,
#             id_rol = %s,
#             fecha_nac = %s,
#             genero = %s,
#             pais_residencia = %s,
#             afiliacion_u = %s,
#             tipo_afiliacion = %s,
#             area_tematica = %s,
#             disciplina_cientifica = %s
#         WHERE id_usuario = %s
#     """
#     values = [
#         nombre,
#         apellido,
#         email,
#         documento,
#         pais_origen,
#         id_rol,
#         fecha_nac,
#         genero,
#         pais_residencia,
#         afiliacion_u,
#         tipo_afiliacion,
#         area_tematica,
#         disciplina_cientifica,
#         id_usuario,
#     ]

#     # --- Rama con cambio de contraseña ---
#     if contrasena and contrasena.strip():
#         query = """
#             UPDATE public.usuarios
#             SET nombre = %s,
#                 apellido = %s,
#                 email = %s,
#                 contrasena = %s,
#                 documento = %s,
#                 pais_origen = %s,
#                 id_rol = %s,
#                 fecha_nac = TO_DATE(%s, 'YYYY-MM-DD'),
#                 genero = %s,
#                 pais_residencia = %s,
#                 afiliacion_u = %s,
#                 tipo_afiliacion = %s,
#                 area_tematica = %s,
#                 disciplina_cientifica = %s
#             WHERE id_usuario = %s
#         """
#         hashed = generate_password_hash(contrasena)
#         values = [
#             nombre,
#             apellido,
#             email,
#             hashed,
#             documento,
#             pais_origen,
#             id_rol,
#             fecha_nac,
#             genero,
#             pais_residencia,
#             afiliacion_u,
#             tipo_afiliacion,
#             area_tematica,
#             disciplina_cientifica,
#             id_usuario,
#         ]

#     conn = get_connection()
#     try:
#         with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
#             cursor.execute(query, values)
#         conn.commit()
#     finally:
#         conn.close()


def actualizar_estudiante(id_usuario, nombre, apellido, email, contrasena, documento, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica):
    base_set = """
        nombre = %s,
        apellido = %s,
        email = %s,
        documento = %s,
        pais_origen = %s,
        id_rol = %s,
        fecha_nac = TO_DATE(%s, 'YYYY-MM-DD'),
        genero = %s,
        pais_residencia = %s,
        afiliacion_u = %s,
        tipo_afiliacion = %s,
        area_tematica = %s,
        disciplina_cientifica = %s
    """

    if contrasena and contrasena.strip():
        hashed = generate_password_hash(contrasena)
        query = f"""
            UPDATE public.usuarios
            SET {base_set},
                contrasena = %s
            WHERE id_usuario = %s
        """
        values = [
            nombre, apellido, email, documento, pais_origen, id_rol, fecha_nac, genero,
            pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica,
            hashed, id_usuario
        ]
    else:
        query = f"""
            UPDATE public.usuarios
            SET {base_set}
            WHERE id_usuario = %s
        """
        values = [
            nombre, apellido, email, documento, pais_origen, id_rol, fecha_nac, genero,
            pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica,
            id_usuario
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
    exitosos = []
    fallidos = []
    id_rol = 3
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for est in lista_estudiantes:
            try:
                conn.rollback()  # limpio posibles restos
                conn.autocommit = False
                # 1) Buscar id_curso por nombre (case‐insensitive)
                cursor.execute(
                    "SELECT id_curso FROM cursos WHERE LOWER(nombre) = LOWER(%s)",
                    (est.get("curso_interes", "").strip(),),
                )
                row = cursor.fetchone()
                if not row:
                    conn.rollback()
                    fallidos.append({
                        "usuario": est,
                        "error": "Curso no encontrado"
                    })
                    continue    
                id_curso = row[0]

                # 2) Verificar duplicados (email o documento)
                cursor.execute("SELECT 1 FROM usuarios WHERE email = %s",
                               (est["email"],))
                if cursor.fetchone():
                    conn.rollback()
                    fallidos.append({"usuario": est, "error": "Usuario ya registrado"})
                    continue

                # Automatizacion contrasena
                # hashed = generate_password_hash(
                #     generar_contrasena(est["apellido"], est["documento"])
                # )

                hashed = generate_password_hash(est["email"]
                )

                from datetime import datetime

                fecha_nac = est.get("fecha_nac")
                if pd.isna(fecha_nac):
                    fecha_nac = None   # se inserta como NULL en la BD
                else:
                    # si viene como Timestamp de pandas
                    if isinstance(fecha_nac, pd.Timestamp):
                        fecha_nac = fecha_nac.date()
                    # si viene como string
                    elif isinstance(fecha_nac, str):
                        try:
                            fecha_nac = datetime.strptime(fecha_nac.strip(), "%Y-%m-%d").date()
                        except:
                            fecha_nac = None

                # 3) Insertar usuario y obtener id_usuario
                cursor.execute(
                    """
                    INSERT INTO Usuarios (nombre, apellido, email, contrasena, pais_origen, id_rol, fecha_nac, genero, pais_residencia, afiliacion_u, tipo_afiliacion, area_tematica, disciplina_cientifica)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id_usuario
                    """,
                    (
                        est["nombre"],
                        est["apellido"],
                        est["email"],
                        hashed,
                        est["pais_origen"],
                        id_rol,
                        fecha_nac,
                        est["genero"],
                        est["pais_residencia"],
                        est["afiliacion_u"],
                        est["tipo_afiliacion"],
                        est["area_tematica"],
                        est["disciplina_cientifica"],
                    ),
                )
                id_usuario = cursor.fetchone()[0]
                # 4) Crear inscripción
                cursor.execute(
                    """
                    INSERT INTO inscripciones (id_usuario,id_curso,fecha_inscripcion,certificado_generado) 
                    VALUES (%s,%s,%s,%s) RETURNING id_inscripcion
                    """,
                    (id_usuario, id_curso,date.today(),False),
                )
                id_insc = cursor.fetchone()[0]

                # 5) Crear nota inicial
                cursor.execute(
                    """INSERT INTO notas (id_inscripcion, nota_final, nota_asistencia, nota_acumulada) 
                    VALUES (%s, %s, %s,%s)
                    """,
                    (id_insc, 0.00, 0.00, 0.00),
                )
                conn.commit()

                # 6) Generar QR automáticamente
                try:
                    qr_filename = generar_qr_estudiante(id_usuario, id_insc, id_curso)
                except Exception as e:
                    qr_filename = None
                    print(f"Error generando QR para usuario {id_usuario}: {e}")

                registro = est.copy()
                registro.update({
                    "id_usuario": id_usuario,
                    "id_inscripcion": id_insc,
                    "qr_path": qr_filename
                })
                exitosos.append(registro)

            except Exception as e:
                conn.rollback()
                registro = est.copy()
                registro["error"] = str(e)
                fallidos.append(registro)

                continue
        return {"exitosos": exitosos, "fallidos": fallidos}
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            cursor.close()
            conn.close()

### Funcion logica de qr
import os
from datetime import datetime
import segno

BASE_DIR = "app/static/qrs"  # ejemplo, donde guardas los QR

def generar_qr_estudiante(id_usuario, id_inscripcion, id_curso):
    os.makedirs(BASE_DIR, exist_ok=True)

    # Evita generar QR duplicados
    existing_files = [
        fname for fname in os.listdir(BASE_DIR)
        if fname.startswith(f"qr_{id_inscripcion}_") and fname.endswith(".png")
    ]
    if existing_files:
        return existing_files[0]  # si ya existe, retornamos el archivo existente

    horario = datetime.now().strftime("%Y-%m-%d %H:%M")
    contenido = (
        f"{os.getenv('URL_APP')}/qrs/registrar?"
        f"id_inscripcion={id_inscripcion}&id_curso={id_curso}"
        f"&id_usuario={id_usuario}&horario={horario}"
    )

    qr = segno.make(contenido)
    filename = f"qr_{id_inscripcion}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    output_file = os.path.join(BASE_DIR, filename)
    qr.save(output_file, scale=10)

    return filename


def eliminar_estudiante(id_usuario):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
        cursor.execute(
            "SELECT id_inscripcion, id_nota FROM inscripciones "
            "JOIN notas USING(id_inscripcion) "
            "WHERE id_usuario = %s",
            (id_usuario,)
        )
        inscripciones = cursor.fetchall()

        for ins in inscripciones:
            id_inscripcion = ins["id_inscripcion"]
            id_nota = ins["id_nota"]
            cursor.execute(
                "DELETE FROM notas WHERE id_inscripcion = %s AND id_nota = %s",
                (id_inscripcion, id_nota)
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return jsonify({"status": "error", "mensaje": f"No se encontró nota {id_nota}"}), 404

            cursor.execute(
                "DELETE FROM inscripciones WHERE id_inscripcion = %s", (id_inscripcion,)
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return jsonify({"status": "error", "mensaje": f"No se encontró inscripcion {id_inscripcion}"}), 404

        # --- 3) Borrar usuario ---
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"status": "error", "mensaje": "No se encontró el usuario"}), 404

        conn.commit()
        return jsonify({"status": "ok", "mensaje": "Usuario, inscripciones y notas eliminadas correctamente"})

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "mensaje": f"Error al eliminar: {e}"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

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
            fecha_nac = TO_DATE(%s, 'YYYY-MM-DD'),
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
                fecha_nac = TO_DATE(%s, 'YYYY-MM-DD'),
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
    exitosos = []
    fallidos = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        id_rol = 2

        for p in lista_ponentes:
            try:
                # 1) Generar y hashear contraseña
                hashed = generate_password_hash(est["email"]
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
                conn.commit()
                exitosos.append({
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
        return {"exitosos": exitosos, "fallidos": fallidos}

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

#PARA USAR EN MAIL
# en tu módulo usu.py (o donde tengas las funciones de DB)

def obtener_estudiantes_i():
    conn = get_connection()
    cur = conn.cursor()
    #cur.execute("""
    #    SELECT u.id_usuario, u.email, i.id_inscripcion
    #    FROM usuarios u
    #    JOIN inscripciones i ON u.id_usuario = i.id_usuario
    #    WHERE u.notificado = FALSE
    #    LIMIT 1
    #""")
    cur.execute("""
        SELECT u.id_usuario, u.email, i.id_inscripcion, CONCAT(u.nombre,' ', u.apellido) as nom, c.nombre as cnombre
        FROM usuarios u
        JOIN inscripciones i ON u.id_usuario = i.id_usuario
		JOIN cursos c ON i.id_curso = c.id_curso
		WHERE u.notificado = FALSE
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Retornar lista de diccionarios
    #estudiantes = [{"id_usuario": r[0], "email": r[1], "id_inscripcion": r[2]} for r in rows]
    estudiantes = [{"id_usuario": r[0], "email": r[1], "id_inscripcion": r[2], "nombre":r[3], "curso":r[4]} for r in rows]
    return estudiantes


def marcar_notificados(ids_usuarios):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        UPDATE usuarios
        SET notificado = TRUE
        WHERE id_usuario = %s
    """
    
    for id_usuario in ids_usuarios:
        cur.execute(query, (id_usuario,))
    
    conn.commit()
    cur.close()
    conn.close()
