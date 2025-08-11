import psycopg2
from app.db_c import get_connection
def obtener_eventos():
    conn = get_connection() # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # crea un cursor (como el "puente" para hacer consultas)
    cursor.execute("SELECT * FROM eventos") # consulta SQL directa
    rows = cursor.fetchall() # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows    # devuelve los datos a quien haya llamado esta función

def obtener_evento(id_evento):
    conn =get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM eventos WHERE id_evento = %s", (id_evento,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def crear_evento(nombre_base):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("INSERT INTO eventos (nombre_base) VALUES (%s) RETURNING id_evento", (nombre_base,))
    id_e = cusor.fetchone()
    conn.commit()
    conn.close()
    return id_e


def actualizar_evento(id_evento, nombre_base):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("UPDATE eventos SET nombre_base = %s WHERE id_evento = %s",
                   (nombre_base, id_evento,))
    conn.commit()
    conn.close()

def eliminar_evento(id_evento):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("DELETE FROM eventos WHERE id_evento = %s", (id_evento,))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


#Version_eventos

def obtener_eventosVs():
    conn = get_connection() # conecta a la base de datos
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # crea un cursor (como el "puente" para hacer consultas)
    cursor.execute("SELECT * FROM version_evento") # consulta SQL directa
    rows = cursor.fetchall() # obtiene todos los resultados en una lista
    conn.close()  # cierra la conexión
    return rows    # devuelve los datos a quien haya llamado esta función
def obtener_eventoVs(id_version):
    conn =get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM version_evento WHERE id_version = %s", (id_version,))
    row = cursor.fetchall()
    conn.close()
    return row

def crear_eventoVs(id_evento, nombre_version, anio, fecha_inicio, fecha_fin, lugar):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("INSERT INTO version_evento (id_evento, nombre_version, anio, fecha_inicio, fecha_fin, lugar) VALUES (%s,%s,%s,%s,%s,%s)", (id_evento, nombre_version, anio, fecha_inicio, fecha_fin, lugar,))
    conn.commit()
    conn.close()

def actualizar_eventoVs(id_evento, nombre_version, anio, fecha_inicio, fecha_fin, lugar, id_version):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("UPDATE version_evento SET id_evento = %s, nombre_version = %s, anio = %s, fecha_inicio = %s, fecha_fin = %s, lugar = %s  WHERE id_version = %s",
                   (id_evento, nombre_version, anio, fecha_inicio, fecha_fin, lugar, id_version,))
    conn.commit()
    conn.close()

def eliminar_eventoVs(id_version):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("DELETE FROM version_evento WHERE id_version = %s", (id_version,))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        conn.rollback()
        return {"status": "error", "mensaje": "Error al eliminar: " + str(e)}


# Evento - Version

def obtener_eventos_full():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT e.id_evento, e.nombre_base, 
               v.id_version, v.nombre_version, v.anio, 
               v.fecha_inicio, v.fecha_fin, v.lugar
        FROM eventos e
        LEFT JOIN version_evento v ON e.id_evento = v.id_evento
        ORDER BY v.anio DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

