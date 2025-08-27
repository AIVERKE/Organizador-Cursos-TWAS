from flask import render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_required
import io
import os
import pandas as pd
import unidecode
import tempfile

from . import rxls_bp
from app import db
from app.models.user import Usuario
from app.controllers import u_controller as usu, c_controller as cur
from app.api.auth.utils import role_required

ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

TIPOS = {
    "estudiantes": ("Estudiantes", usu.crear_estudiantes_con_inscripcion_con_lote),
    "ponentes":    ("Ponentes",    usu.crear_ponentes_con_lote),
    "cursos":      ("Cursos",      cur.crear_cursos_con_lote),
}

PLANTILLAS = {
    "estudiantes": {
        "columnas": ["nombre", "apellido", "email", "documento", "pais_origen",
                     "fecha_nac", "genero", "pais_residencia", "afiliacion_u",
                     "tipo_afiliacion", "area_tematica", "disciplina_cientifica", 
                     "nombre_curso", "modalidad"],
        "ejemplo": ["Juan", "Perez", "juan@mail.com", "123456", "Bolivia",
                    "2000-01-01", "male", "Bolivia", "Universidad X", "public", 
                    "Ciencias", "Matemática", "Curso 1", "Virtual"]
    },
    "ponentes": {
        "columnas": ["nombre", "apellido", "email", "documento", "pais_origen",
                     "fecha_nac", "genero", "pais_residencia", "afiliacion_u",
                     "tipo_afiliacion", "area_tematica", "disciplina_cientifica"],
        "ejemplo": ["Ana", "Gomez", "ana@mail.com", "987654", "Bolivia",
                    "1990-05-05", "female", "Bolivia", "Universidad Y", "private", 
                    "Ciencias", "Física"]
    },
    "cursos": {
        "columnas": ["nombre", "descripcion", "modalidad"],
        "ejemplo": ["Curso 1", "Descripción ejemplo", "Presencial"]
    }
}

# Funciones de ayuda
def save_temp_df(df):
    """Guarda el DataFrame en un archivo temporal (pickle) y devuelve la ruta."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
    tmp.close()
    df.to_pickle(tmp.name)
    return tmp.name
def load_temp_df(path):
    """Carga un DataFrame desde la ruta guardada."""
    return pd.read_pickle(path)

def remove_temp_file(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
def leer_y_normalizar(file, tipo):
    """
    Lee un FileStorage (CSV/XLSX), normaliza cabeceras y valores críticos.
    Devuelve (df, errores_list).
    """
    if not file or not getattr(file, "filename", None):
        return None, ["No se envió archivo"]

    filename = file.filename
    if not allowed_file(filename):
        return None, ["Extensión no permitida (usar xlsx/xls/csv)"]

    ext = filename.rsplit(".", 1)[1].lower()

    # función interna para probar varios encodings en CSV
    def _read_csv_stream(stream):
        for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
            try:
                stream.seek(0)
                df_ = pd.read_csv(stream, encoding=enc)
                return df_
            except Exception:
                continue
        raise ValueError("No se pudo leer CSV con encodings comunes")

    try:
        # Leer archivo
        if ext == "csv":
            # file.stream es file-like
            df = _read_csv_stream(file.stream)
        else:
            # Excel: leer primera hoja por defecto; mantener strings para campos como documento
            file.stream.seek(0)
            df = pd.read_excel(file.stream, sheet_name=0, dtype=str)
    except Exception as e:
        return None, [f"Error al leer archivo: {e}"]

    # Normalizar cabeceras: strip, lower, quitar tildes
    df.columns = df.columns.str.strip().str.lower().map(unidecode.unidecode)

    # Forzar columnas críticas a string (evita pérdida de ceros)
    for c in ("documento", "email"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Trim general de strings
    df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)

    # Reemplazar valores NaN por None para evitar problemas al serializar
    df = df.where(pd.notnull(df), None)

    # Validar columnas obligatorias
    required = PLANTILLAS[tipo]["columnas"]
    faltantes = [c for c in required if c not in df.columns]
    if faltantes:
        return None, [f"Faltan columnas: {', '.join(faltantes)}"]

    # Normalizaciones específicas
    if "fecha_nac" in df.columns:
        # intenta parsear con dayfirst=True (dd/mm/yyyy)
        df["fecha_nac"] = pd.to_datetime(df["fecha_nac"], errors="coerce", dayfirst=True)

    if "genero" in df.columns:
        df["genero"] = df["genero"].astype(str).str.strip().str.lower().map({
            "masculino": "male", "m": "male", "male": "male",
            "femenino": "female", "f": "female", "female": "female"
        }).where(df["genero"].notnull(), None)

    if "email" in df.columns:
        df["email"] = df["email"].astype(str).str.strip().str.lower()

    return df, []

@rxls_bp.route('/', defaults={'tipo': 'estudiantes'}, methods=['GET', 'POST'])
@rxls_bp.route("/<tipo>", methods=["GET","POST"])
@login_required
@role_required(1, 4)
def index(tipo):
    if tipo not in TIPOS:
        flash("Tipo no válido.","danger")
        return redirect(url_for("rxls.index", tipo="estudiantes"))

    titulo, func_guardar = TIPOS[tipo]
    tabla_html,fallidos,exitosos = None,[],[]


    # Si quieres mostrar últimos guardados en la vista:
    if session.get("ultimo_guardado") and session["ultimo_guardado"].get("tipo") == tipo:
        fallidos = session["ultimo_guardado"].get("fallidos", [])
        exitosos = session["ultimo_guardado"].get("exitosos", [])

    if request.method == "POST":
        accion = request.form.get("accion")
        file   = request.files.get("file")

        if accion == "vista":

            df, errores = leer_y_normalizar(file,tipo)
            if errores:
                flash("Errores al procesar: " + "; ".join(errores), "danger")
                return redirect(request.url)

            # Guardar DF en temp file y guardar path en session
            tmp_path = save_temp_df(df)
            session["tmp_df_path"] = tmp_path

            # Crear tabla HTML de preview (solo primeras N filas)
            tabla_html = df.head(200).to_html(classes="table table-striped", index=False, border=0)

            flash("Archivo leído correctamente. Revisa la vista previa antes de guardar.", "success")
            return render_template(
                "readxls/readxls.html",
                titulo=titulo,
                tipo=tipo,
                tabla=tabla_html,
                fallidos=fallidos,
                exitosos=exitosos,
                columnas_recomendadas=PLANTILLAS[tipo]["columnas"],
                ejemplo_fila=PLANTILLAS[tipo]["ejemplo"]
            )

        elif accion == "guardar":
            # Cargar DF desde temp path en session
            tmp_path = session.get("tmp_df_path")
            if not tmp_path or not os.path.exists(tmp_path):
                flash("No hay datos temporales para guardar. Vuelve a cargar el archivo.", "warning")
                return redirect(request.url)

            try:
                df = load_temp_df(tmp_path)
                # pasar a lista de dicts al controlador
                data = df.to_dict("records")
                resultado = func_guardar(data)  # {"registrados": [...], "fallidos": [...]}
                registrados = resultado.get("registrados", [])
                fallidos = resultado.get("fallidos", [])

                session["ultimo_guardado"] = {
                    "tipo": tipo,
                    "exitosos": exitosos,
                    "fallidos": fallidos
                }
                # limpiar temp
                remove_temp_file(tmp_path)
                session.pop("df_data", None)

                if fallidos:
                    flash(f"{len(fallidos)} registros fallidos.", "warning")
                if exitosos:
                    flash(f"{len(exitosos)} registros guardados correctamente.", "success")
                return redirect(url_for("rxls.index", tipo=tipo))

            except Exception as e:
                # intentar borrar temp igualmente
                remove_temp_file(tmp_path)
                session.pop("tmp_df_path", None)
                flash(f"Error al guardar {titulo}: {e}", "danger")
                return redirect(request.url)
    
    return render_template(
        "readxls/readxls.html",
        titulo=titulo,
        tipo=tipo,
        tabla=tabla_html,
        fallidos=fallidos,
        exitosos=exitosos,
        columnas_recomendadas=PLANTILLAS[tipo]["columnas"],
        ejemplo_fila=PLANTILLAS[tipo]["ejemplo"]
    )

# --- DESCARGA DE EXCELS ---
def send_df_excel(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return send_file(output, download_name=filename, as_attachment=True)

@rxls_bp.route("/descargar/exitosos/<tipo>")
@login_required
@role_required(1, 4)
def descargar_exitosos(tipo):
    if "ultimo_guardado" not in session or session["ultimo_guardado"].get("tipo") != tipo:
        flash("No hay registros guardados para descargar.", "warning")
        return redirect(url_for("rxls.index", tipo=tipo))

    exitosos = session["ultimo_guardado"].get("exitosos", [])
    if not exitosos:
        flash("No hay registros exitosos para descargar.", "info")
        return redirect(url_for("rxls.index", tipo=tipo))

    df = pd.json_normalize(exitosos)
    return send_df_excel(df, f"{tipo}_exitosos.xlsx")

@rxls_bp.route("/descargar/fallidos/<tipo>")
@login_required
@role_required(1, 4)
def descargar_fallidos(tipo):
    if "ultimo_guardado" not in session or session["ultimo_guardado"].get("tipo") != tipo:
        flash("No hay registros guardados para descargar.", "warning")
        return redirect(url_for("rxls.index", tipo=tipo))

    fallidos = session["ultimo_guardado"].get("fallidos", [])
    if not fallidos:
        flash("No hay registros fallidos para descargar.", "info")
        return redirect(url_for("rxls.index", tipo=tipo))

    df = pd.json_normalize(fallidos)
    return send_df_excel(df, f"{tipo}_fallidos.xlsx")

@rxls_bp.route("/descargar/plantilla/<tipo>")
@login_required
@role_required(1, 4)
def descargar_plantilla(tipo):
    if tipo not in PLANTILLAS:
        flash("Tipo no válido.", "warning")
        return redirect(url_for("rxls.index", tipo="estudiantes"))
    cols = PLANTILLAS[tipo]["columnas"]
    ejemplo = PLANTILLAS[tipo]["ejemplo"]

    df = pd.DataFrame([ejemplo], columns=cols)
    return send_df_excel(df, f"plantilla_{tipo}.xlsx")