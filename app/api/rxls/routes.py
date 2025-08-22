from flask import render_template, request, redirect, url_for, flash, session
import pandas as pd
import io

from . import rxls_bp
from app import db
from app.models.user import Usuario
from flask_login import login_required
from app.controllers import u_controller as usu
from app.controllers import c_controller as cur
from app.api.auth.utils import role_required

ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

TIPOS = {
    "estudiantes": ("Estudiantes", usu.crear_estudiantes_con_inscripcion_con_lote),
    "ponentes":    ("Ponentes",    usu.crear_ponentes_con_lote),
    "cursos":      ("Cursos",      cur.crear_cursos_con_lote),
}

@rxls_bp.route('/', defaults={'tipo': 'estudiantes'}, methods=['GET', 'POST'])
@rxls_bp.route("/<tipo>", methods=["GET","POST"])
@login_required
@role_required(1, 4)
def index(tipo):
    if tipo not in TIPOS:
        flash("Tipo no válido.")
        return redirect(url_for("rxls.index", tipo="estudiantes"))

    if tipo == "estudiantes":
        columnas_recomendadas = ["nombre", "apellido", "email", "documento", "pais_origen", "fecha_nac", "genero", "pais_residencia", "afiliacion_u", "tipo_afiliacion", "area_tematica", "disciplina_cientifica", "nombre_curso", "modalidad"]
        ejemplo_fila = ["Juan", "Perez", "juan@email.com", "12345678", "Bolivia", "1995-01-01", "M", "Bolivia", "Universidad X", "Estudiante", "Ciencias", "Física", "Matemáticas Básicas", "Presencial"]
    elif tipo == "ponentes":
        columnas_recomendadas = ["nombre", "apellido", "email", "documento", "pais_origen", "fecha_nac", "genero", "pais_residencia", "afiliacion_u", "tipo_afiliacion", "area_tematica", "disciplina_cientifica"]
        ejemplo_fila = ["Ana", "Gomez", "ana@email.com", "87654321", "Bolivia", "1980-05-05", "F", "Bolivia", "Universidad Y", "Ponente", "Ingeniería", "Electrónica"]
    elif tipo == "cursos":
        columnas_recomendadas = ["nombre", "descripcion", "modalidad", "id_version", "id_ponente"]
        ejemplo_fila = ["Curso X", "Descripción del curso", "Presencial", "1", "1"]

    titulo, guardar_fn = TIPOS[tipo]
    tabla_html = None

    fallidos = []
    exitosos = []

    if session.get("ultimo_guardado") and session["ultimo_guardado"].get("tipo") == tipo:
        # Solo mostrar los datos de este tipo
        fallidos = session["ultimo_guardado"].get("fallidos", [])
        exitosos = session["ultimo_guardado"].get("exitosos", [])

    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "vista":
            file   = request.files.get("file")

            if not file or not allowed_file(file.filename):
                flash("Archivo no válido o no recibido.")
                return redirect(request.url)

            # Leer y almacenar JSON en sesión para vista previa
            ext = file.filename.rsplit(".",1)[1].lower()
            df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)
            df.columns = df.columns.str.strip().str.lower()
            session["df_data"] = df.to_json()
            tabla_html = df.to_html(classes="table table-bordered", index=False, border=0)
            flash("Archivo leído correctamente.")

        elif accion == "guardar":
            if "df_data" not in session:
                flash("No hay datos para guardar.")
                return redirect(request.url)
            try:
                data = pd.read_json(io.StringIO(session["df_data"])).to_dict("records")
                resultado = guardar_fn(data)  # ahora tus controladores retornan {"exitosos": [...], "fallidos": [...]}
                exitosos = resultado.get("registrados", [])
                fallidos  = resultado.get("fallidos", [])

                session["ultimo_guardado"] = {
                    "tipo": tipo,
                    "exitosos": exitosos,
                    "fallidos": fallidos
                }
                session.pop("df_data", None)

                msg = f"{len(exitosos)} registros guardados correctamente."
                if fallidos:
                    msg += f" {len(fallidos)} fallaron."
                    # Opcional: mostrar detalles de fallidos en flash
                    detalle_fallidos = ", ".join([str(f) for f in fallidos])
                    flash(f"Fallidos: {detalle_fallidos}", "warning") 
                flash(msg, "success")
                return redirect(url_for("rxls.index", tipo=tipo))
            except Exception as e:
                flash(f"Error al guardar {titulo}: {e}")
                return redirect(request.url)
    return render_template(
        "readxls/readxls.html",
        titulo=titulo,
        tipo=tipo,
        tabla=tabla_html,
        fallidos=fallidos,  # nuevos
        exitosos=exitosos,   # opcional
        columnas_recomendadas=columnas_recomendadas,
        ejemplo_fila=ejemplo_fila
    )

from flask import send_file

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

    df = pd.DataFrame(exitosos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Exitosos")
    output.seek(0)
    return send_file(output, download_name=f"{tipo}_exitosos.xlsx", as_attachment=True)


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

    df = pd.DataFrame(fallidos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Fallidos")
    output.seek(0)
    return send_file(output, download_name=f"{tipo}_fallidos.xlsx", as_attachment=True)

