# Proyecto Administracion de Eventos Educativos

## Descripción General
Proyecto Administracion de Eventos Educativos es una aplicación web para la gestión de eventos educativos a nivel corporativo. Permite la organizar y consultar actividades académicas de manera intuitiva y sencilla, ante la necesidad de coordinadores de eventos académicos que requieran una herramienta amigable para el manejo de la misma.
Sigue una estructura progesional y escalable, con FLask y PostgreSQL como herramientas principales.


## Caracteristicas Principales
Este proyecto permite las procesos de:
- Gestión de Eventos: Crear, editar y eliminar eventos
- Gestión de Cursos o Actividades: Gestión creación, actualizacion y eliminación de actividades académicas relacionadas con distintos eventso.
- Gestion de asistentes: Registro, listado, seguimiento de asistencias, gestión de notas y certificados de usuarios.
- Interfaz Web Responsiva: Páginas con plantillas HTML/CSS para visualización en dispositivos de escritorio, moviles o portátiles.

## Tecnologías Utilizadas

Leguaje Base:
	- Python 3.11: Lenguaje de programación principal para el backend de la aplicación web.

BackEnd y Lógica del Servidor
	- Flask: Framework web ligero para Python que permite construir aplicaciones web con facilidad. Es responsable de manejar las rutas, solicitudes HTTP y lógica del servidor.
	- Flask-Login: Maneja la autenticación de usuarios (login/logout), control de sesiones 
	y protección de rutas según roles.
	- Flask-Mail: Permite enviar correos electrónicos desde la aplicación.
	- Flask-SQLAlchemy: Extensión que facilita el uso de bases de datos con SQLAlchemy dentro de Flask, permitiendo trabajar con modelos ORM (Mapeo Objeto-Relacional).
	- SQLAlchemy: Toolkit SQL y ORM que permite interactuar con la base de datos usando objetos en lugar de escribir consultas SQL manuales.
	- Werkzeug: Utilidad subyacente de Flask para manejar el enrutamiento, peticiones HTTP y servidores de desarrollo.
	- python-dotenv / dotenv: Permite cargar variables de entorno desde un archivo .env para manejar configuraciones sensibles como claves secretas, contraseñas o puertos.

Base de Datos:
	- PostgreSQL: Sistema de gestión de bases de datos relacional utilizado para almacenar la información de usuarios, eventos, registros, etc.
	- psycopg2: Librería que permite a Python conectarse y trabajar con bases de datos PostgreSQL.

FrontEnd:
	- HTML/CSS: Creación y diseño de las interfaces de usuarios (estudiantes, exponentes y coordinadores)
	- JavaScript: Lenguaje de scripting que mejora la interactividad de la aplicación.

Datos y Visualización:
	- pandas: Librería de análisis y manipulación de datos en Python; útil para procesar archivos Excel/CSV u otros datos tabulares.
	- numpy: Biblioteca fundamental para cálculos numéricos en Python.
	- openpyxl: Permite leer y escribir archivos de Excel (.xlsx).
	- fpdf: Librería para generar archivos PDF (por ejemplo, comprobantes de inscripción, reportes de eventos).

Utilidades Adicionales:
	- Jinja2: Motor de plantillas de Flask. Permite incrustar variables de Python dentro de archivos HTML y generar contenido dinámico.
	- MarkupSafe / itsdangerous: Utilidades de seguridad para proteger formularios y datos firmados.
	- segno: Permite generar códigos QR en la aplicación.
	- blinker: Sistema de señales usado internamente por Flask para enviar notificaciones entre partes de la aplicación.
	- python-dateutil: Gestión de fechas.

## Instalación 
Sigue estos pasos para preparar el entorno de desarollo:
1. Clonación de Repositorio
`
git clone https://github.com/AlanMC7650/AplicacionCertificados.git
cd AplicacionCertificados
`

2. Crear entorno virtual e instalar dependencias:
`
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
`

3. Configurar base de datos: Ejecutar los comandos SQL o usar migraciones para crear la base de datos.
`
psql -U postgres < sql.sql
database/init_db.sql o scripts_sql/estructura_inicial.sql
`

4. Ajustes iniciales: Copiar el archivo de ejemplo de configuración de entorno (patuEnv.txt) y editar variables.
`cp patuEnv.txt .env`

## Configuración
Antes de ejecutar la aplicación, define las variables de entorno necesarias (en un archivo .env bajo la plantilla 'patuEnv.txt'), de modo que no queden hardcodeadas en el código. 
Las variables típicas son:

- DB_HOST, DB_NAME, DB_USER, DB_PASSWORD: Credenciales de la base de datos PostgreSQL.
- FLASK_ENV: Entorno de Flask (development o production).
- SECRET_KEY: Clave secreta para sesiones o formularios CSRF.
- MAIL_SERVER, MAIL_PORT, etc.: Configuración del servidor SMTP (si hay notificaciones por correo).

Por ejemplo, el archivo .env podría contener:
`
FLASK_ENV=development
DATABASE_URL=postgresql://{tu_usuario_postgres}:{tu_contraseña}@localhost:5432/{tu_base_de_datos}
SECRET_KEY=mi_clave_segura_1234
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=correo_username@example.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
`
Flask (con python-dotenv) cargará estas variables automáticamente al iniciar la aplicación.

## Uso Básico
Con el entorno activado y configurado, ejecutar la aplicación de desarrollo de la siguiente manera, para un trabajo local:
`
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
`
Luego abrir http://localhost:5000 en el navegador. Se mostrará la página de inicio del proyecto.

## Desarollo y Despliegue
-- pendientes

## Estructura del Proyecto

```plaintext
AplicacionCertificados/
├── app/
│   ├── api/
│   │   ├── auth/
│   │   │	├── __init__.py
│   │   │	├── forms.py
│   │   │	├── routes.py
│   │   │	└── utils.py
│   │   ├── certificate/
│   │   │	├── Input/
│   │   │	│	└── certificate_template.jpg
│   │   │	├── __init__.py
│   │   │	├── routes.py
│   │   │	└── utils.py
│   │   ├── coordinador/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── cursos/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── eventos/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── home/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── inscripciones/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── qrs/
│   │   │	├── __init__.py
│   │   │	├── routes.py
│   │   │	└── utils.py
│   │   ├── qrscan/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   ├── rxls/
│   │   │	├── __init__.py
│   │   │	└── routes.py
│   │   └── usuarios/
│   │   	├── __init__.py
│   │   	└── routes.py
│   ├── controllers/
│   │   ├── c_controller.py
│   │   ├── e_controller.py
│   │   ├── i_controller.py
│   │   └── u_controller.py
│   ├── static/
│   │	├── css/
│   │   │	├── Coordinador/
│	│   │   │	└── styleCoordinador.css
│   │   │	├── Estudiante/
│	│   │   │	├── styleCurso.css
│	│   │   │	└── styleEstudiante.css
│   │   │	├── Expositor/
│	│   │   │	├── calificacionExp.css
│	│   │   │	├── CursosExp.css
│	│   │   │	├── datosPersonalesExp.css
│	│   │   │	└── styleExpositor.css
│   │   │	├── password-chech.css
│   │   │	├── styleinicio.css
│   │   │	└── styleLogin.css
│   │	├── images/
│   │   │	├── cuere.png
│   │   │	├── Flag_of_UNESCO.png
│   │   │	├── logo-UNESCO.png
│   │   │	├── org1.png
│   │   │	├── org2.png
│   │   │	├── org3.png
│   │   │	├── PaisajeIllimani.png
│   │   │	├── umsalogo.png
│   │   │	└── Unesco-TWAS.jpg
│   │	├── js/
│   │   │	├── controlAsistencia.js
│   │   │	├── cursoAsistenciaProvivional.js
│   │   │	├── estudianteControl.js
│   │   │	└── password-chech.js
│   │	└── qrs/
│   ├── temp_certificates/
│   ├── templates/
│   │   ├── Coordinador/
│   │   │	├── partials/
│   │   │	│	├── cursos.html
│   │   │	│	├── estudiantes.html
│   │   │	│	├── eventos.html
│   │   │	│	└── expositores.html
│   │   │	└── indexCoordinador.html
│   │   ├── Estudiante/
│   │   │	├── Curso.html
│   │   │	└── Estudiante.html
│   │   ├── Expositor/
│   │   │	├── calificacionExp.html
│   │   │	├── CursoExp.html
│   │   │	├── datosPersonalesExp.html
│   │   │	└── expositor.html
│   │   ├── ForgotPassword/
│   │   │	├── ForgotPassword.html
│   │   │	├── ForgotPasswordAlert.html
│   │   │	└── ForgotPasswordverificado.html
│   │   ├── hechopormichael/
│   │   │	├── reset_password.html
│   │   │	├── send_bulk_certificate.html
│   │   │	└── send_certificate.html
│   │   ├── qrscan/
│   │   │	└── scan.html
│   │   ├── readxls/
│   │   │	└── readxls.html
│   │   ├── user/
│   │   │	└── profile.html
│   │	├── dashboard.html
│   │	├── index.html
│   │	└── login.html	
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── db_c.py
│   ├── extensions.py
│   ├── requirements.txt
│   └── run.py
├── .gitignore
├── README.md        
├── docker-composer.yml
├── insertar_usuarios.py
├── manage.py
├── patuEnv.txt
└── requirements.txt	      
```

## Autor
BattleBreadCOso – GitHub/alanmc... – bbread@ejemplo.com. Creó esta aplicación como proyecto en grupo. Para dudas o comentarios, puedes contactar por correo o abrir un issue en GitHub.

## Licencia
Este proyecto está licenciado bajo la Battle_Bread_License. 