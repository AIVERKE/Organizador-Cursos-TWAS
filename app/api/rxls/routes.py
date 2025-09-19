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

import json
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
        "columnas": [
            "nombre / first name",
            "apellido / surname",
            "direccion de correo electronico",
            "fecha de nacimiento",
            "genero / gender",
            "pais de origen",
            "pais de residencia actual / country of residence",
            "afiliacion - instituto o universidad a la que pertenece actualmente / affiliation-institution",
            "tipo de afiliacion / type of affiliation",
            "area tematica field of knowledge",
            "disciplina cientifica",
            "seleccione solo un curso de su interes",
        ],
        "ejemplo": ["Juan", "Perez", "juan@mail.com", "2000-01-01",
                    "male", "Bolivia", "Bolivia", "Universidad X", 
                    "public", "Ciencias", "Matemática", "Curso 1"]
    },
    "ponentes": {
        "columnas": [
            "nombre / first name",
            "apellido / surname",
            "direccion de correo electronico",
            "fecha de nacimiento",
            "genero / gender",
            "pais de origen",
            "pais de residencia actual / country of residence",
            "afiliacion - instituto o universidad a la que pertenece actualmente / affiliation-institution",
            "tipo de afiliacion / type of affiliation",
            "area tematica field of knowledge",
            "disciplina cientifica",
        ],
        "ejemplo": ["Ana", "Gomez", "ana@mail.com", "1990-05-05",
            "female", "Bolivia", "Bolivia", "Universidad Y", 
            "private", "Ciencias", "Física"]
    },
    "cursos": {
        "columnas": ["nombre de curso / course name", "descripcion / description", "modalidad / modality"],
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
    DB_COLUMN_MAPPING = {
        "nombre / first name": "nombre",
        "apellido / surname": "apellido",
        "direccion de correo electronico": "email",
        "fecha de nacimiento": "fecha_nac",
        "genero / gender": "genero",
        "pais de origen": "pais_origen",
        "pais de residencia actual / country of residence": "pais_residencia",
        "afiliacion - instituto o universidad a la que pertenece actualmente / affiliation-institution": "afiliacion_u",
        "tipo de afiliacion / type of affiliation": "tipo_afiliacion",
        "area tematica field of knowledge": "area_tematica",
        "disciplina cientifica": "disciplina_cientifica",
        "seleccione solo un curso de su interes": "curso_interes",
        "nombre de curso / course name": "nombre_curso",
        "descripcion / description": "descripcion",
        "modalidad / modality": "modalidad",
    }



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

    # Normalizar cabeceras: strip, lower, quitar tildes y eliminar paréntesis
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .map(unidecode.unidecode)
        .str.replace(r'\(.*\)', '', regex=True)
        .str.replace(':', '', regex=False)
        .str.replace(')', '', regex=False)
        .str.replace('(', '', regex=False)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )
    # Usar flash con JSON
    #cols_list = df.columns.tolist()
    #flash(json.dumps(cols_list))

    # Renombrar las columnas usando el mapeo
    df.rename(columns=DB_COLUMN_MAPPING, inplace=True, errors='ignore')

    # Trim general de strings
    df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)

    # Validar columnas obligatorias
    required_db_names = [DB_COLUMN_MAPPING.get(c, c) for c in PLANTILLAS[tipo]["columnas"]]
    required_db_names = [unidecode.unidecode(col).lower().strip() for col in required_db_names]
    df_cols = [unidecode.unidecode(col).lower().strip() for col in df.columns]
    #flash(json.dumps(df_cols))
    #flash(json.dumps(required_db_names))
    #flash(json.dumps(DB_COLUMN_MAPPING))
    #flash(json.dumps(PLANTILLAS[tipo]["columnas"]))

    faltantes = [c for c in required_db_names if c not in df_cols]

    if faltantes:
        return None, [f"Faltan columnas: {', '.join(faltantes)}"]

    # ---- Normalizaciones según tipo ----
    if tipo in ("estudiantes", "ponentes"):
        # Capitalizar nombre y apellido
        if "nombre" in df.columns:
            df["nombre"] = df["nombre"].astype(str).str.strip().str.title()

        if "apellido" in df.columns:
            df["apellido"] = df["apellido"].astype(str).str.strip().str.title()

        #if "documento" in df.columns:
        #    df["documento"] = df["documento"].astype(str).str.strip()
        if "email" in df.columns:
            df["email"] = df["email"].astype(str).str.strip().str.lower()
        if "fecha_nac" in df.columns:
            df["fecha_nac"] = pd.to_datetime(df["fecha_nac"], errors="coerce", dayfirst=True)
            df["fecha_nac"] = df["fecha_nac"].dt.strftime("%Y-%m-%d")
        if "genero" in df.columns:
            df["genero"] = df["genero"].astype(str).str.strip().str.lower().map({
                "masculino": "male", "m": "male", "male": "male", "masculino (male)":"male",
                "femenino": "female", "f": "female", "female": "female","femenino (female)":"female"
            }).where(df["genero"].notnull(), None)
        if "tipo_afiliacion" in df.columns:
            df["tipo_afiliacion"] = df["tipo_afiliacion"].astype(str).str.strip().str.lower().map({
                "publica": "public", "publico": "public", "público":"public", "pública":"public",
                "privada": "private", "privado": "private"
            }).where(df["tipo_afiliacion"].notnull(), None)
        if "curso_interes" in df.columns:
            df[["curso_es", "curso_en"]] = df["curso_interes"].str.split("/", n=1, expand=True)
            df["curso_es"] = df["curso_es"].str.strip()
            df["curso_en"] = (
                df["curso_en"]
                .fillna("")  
                .str.strip()
                .str.replace(r"\)$", "", regex=True)
            )

            df["curso_interes"] = df["curso_es"]

    elif tipo == "cursos":
        if "modalidad" in df.columns:
            df["modalidad"] = df["modalidad"].astype(str).str.strip().str.lower()
            # ejemplo: "virtual", "presencial" → "Virtual", "Presencial"

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

                for col in df.columns:
                    if "fecha" in col:
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                        df[col] = df[col].dt.strftime("%Y-%m-%d")
                        df[col] = df[col].replace("NaT", None)
                # pasar a lista de dicts al controlador
                data = df.to_dict("records")
                resultado = func_guardar(data)
                exitosos = resultado.get("exitosos", [])
                fallidos = resultado.get("fallidos", [])

                session["ultimo_guardado"] = {
                    "tipo": tipo,
                    "exitosos": exitosos,
                    "fallidos": fallidos
                }
                # limpiar temp
                remove_temp_file(tmp_path)
                session.pop("tmp_df_path", None)

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
    
    #flash(exitosos)
    #flash(fallidos)
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

# Mapeo de nombres de la base de datos a los de la plantilla
TEMPLATE_COLUMN_MAPPING = {
    "usuario_nombre": "nombre / first name",
    "usuario_apellido": "apellido / surname",
    "usuario_email": "direccion de correo electronico",
    "usuario_fecha_nac": "fecha de nacimiento",
    "usuario_genero": "genero / gender",
    "usuario_pais_origen": "pais de origen",
    "usuario_pais_residencia": "pais de residencia actual / country of residence",
    "usuario_afiliacion_u": "afiliacion - instituto o universidad a la que pertenece actualmente / affiliation-institution",
    "usuario_tipo_afiliacion": "tipo de afiliacion / type of affiliation",
    "usuario_area_tematica": "area tematica field of knowledge",
    "usuario_disciplina_cientifica": "disciplina cientifica",
    "usuario_curso_interes": "seleccione solo un curso de su interes",
    "id_inscripcion": "id_inscripcion",
    "id_usuario": "id_usuario",
    "qr_path": "qr_path",
    "error" : "error",
}

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

    # Normalizar los datos a DataFrame
    #df = pd.json_normalize(exitosos)
    df = pd.json_normalize(exitosos, sep="_")  # 'usuario.nombre' → 'usuario_nombre'
    #df = pd.json_normalize(exitosos, record_path=None, meta=None)
    
    # Renombrar las columnas a los nombres de la plantilla
    df.rename(columns=TEMPLATE_COLUMN_MAPPING, inplace=True, errors='ignore')

    # Reordenar las columnas para que coincidan con la plantilla
    required_cols = PLANTILLAS[tipo]["columnas"]
    extra_cols = ["id_inscripcion", "id_usuario", "qr_path"]
    all_cols = required_cols + [c for c in extra_cols if c not in required_cols]
    df = df[[c for c in all_cols if c in df.columns]]
    df = df.reindex(columns=all_cols)

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

    # Normalizar los datos a DataFrame
    df = pd.json_normalize(fallidos)
    df = pd.json_normalize(fallidos, sep="_")
    # Renombrar las columnas a los nombres de la plantilla
    df.rename(columns=TEMPLATE_COLUMN_MAPPING, inplace=True, errors='ignore')

    # Reordenar las columnas para que coincidan con la plantilla
    required_cols = PLANTILLAS[tipo]["columnas"]
    extra_cols = ["error"]
    all_cols = required_cols + [c for c in extra_cols if c not in required_cols]
    df = df[[c for c in all_cols if c in df.columns]]
    df = df.reindex(columns=all_cols)

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