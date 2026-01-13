# Sistema de Gestión de Catequesis (MongoDB) - Fase 7

Este repositorio contiene la implementación de la **Fase 7 del Proyecto Integrador**. Se trata de una aplicación web completa desarrollada en **Python** con **Flask**, diseñada para interactuar con una base de datos NoSQL en la nube (**MongoDB Atlas**).

## 📋 Descripción del Proyecto

El sistema permite la administración digital de una parroquia, gestionando el ciclo de vida de la catequesis: desde el registro del estudiante hasta el control diario de asistencias. 

La aplicación destaca por implementar patrones de diseño NoSQL, como la **desnormalización** y el manejo de **identificadores híbridos** (soporte simultáneo para IDs numéricos migrados de SQL y ObjectIds nativos de MongoDB).

## 👥 Integrantes (Grupo 6)
* **Mullo, Josue**
* **Solorzano, Camily**
* **Navarrete, Jeffrey**

---

## 🚀 Tecnologías Utilizadas
* **Lenguaje:** Python 3.x
* **Backend Framework:** Flask
* **Base de Datos:** MongoDB Atlas (Nube)
* **Driver:** PyMongo
* **Frontend:** HTML5, Jinja2, Bootstrap 5

---

## ✨ Funcionalidades Principales

### 1. Módulo de Estudiantes (CRUD Completo)
* **Registrar:** Validación automática de duplicados (captura de error `DuplicateKeyError` en cédulas).
* **Consultar:** Listado general de estudiantes.
* **Editar:** Modificación de datos personales.
* **Eliminar:** Borrado lógico y físico de registros.

### 2. Gestión de Grupos
* Creación de cursos asignando Parroquia, Nivel y Catequista.
* Visualización de tarjetas informativas con contador de alumnos en tiempo real.

### 3. Inscripciones (Lógica NoSQL Avanzada)
* Vinculación de Estudiantes con Grupos.
* **Desnormalización:** Al inscribir un alumno, el sistema actualiza automáticamente el documento del `Grupo`, agregando al estudiante en un array interno (`alumnos`). Esto optimiza la velocidad de lectura.

### 4. Control de Asistencias
* Selección de grupo y visualización de nómina.
* Registro masivo de estados (Presente/Ausente/Justificado).
* Historial de sesiones.

---

## 📂 Estructura del Proyecto

```text
Proyecto_Fase7/
│
├── app.py                # Controlador principal (Lógica de negocio y Rutas)
├── requirements.txt      # Lista de dependencias del proyecto
├── README.md             # Documentación del proyecto
│
└── templates/            # Vistas (Interfaz de Usuario HTML/Bootstrap)
    ├── base.html         # Plantilla base (Navbar y Footer)
    ├── index.html        # Pantalla de inicio (Dashboard)
    ├── registro.html     # Formulario de estudiantes
    ├── consultas.html    # Tablas de visualización
    ├── grupos.html       # Gestión de grupos
    ├── inscripciones.html # Gestión de inscripciones
    ├── asistencia_*.html # Módulos de toma de lista
    └── ...

🛠️ Instrucciones de Instalación
Si deseas ejecutar este proyecto en tu máquina local:

Clonar el repositorio:

Bash

git clone [https://github.com/sekai882/GestionCatequesis-Grupo6.git](https://github.com/sekai882/GestionCatequesis-Grupo6.git)
cd GestionCatequesis-Grupo6
Crear un entorno virtual (Opcional pero recomendado):

Bash

python -m venv venv
# En Windows:
venv\Scripts\activate
Instalar dependencias: Asegúrate de tener el archivo requirements.txt y ejecuta:

Bash

pip install -r requirements.txt
Configurar Base de Datos: El proyecto ya cuenta con la cadena de conexión a MongoDB Atlas configurada en app.py. Asegúrate de tener acceso a internet.

Ejecutar la aplicación:

Bash

python app.py
Abrir en el navegador: Ve a http://127.0.0.1:5000

📝 Notas Adicionales
La aplicación maneja validaciones de seguridad básicas.

Se utiliza Bootstrap 5 para garantizar que la interfaz sea responsiva y amigable.

El manejo de errores incluye bloques try-except para evitar caídas del servidor ante datos inconsistentes.


### Un detalle extra importante

Para que el paso 3 de las instrucciones funcione, necesitas crear un archivo llamado `requirements.txt` en tu carpeta. Si no lo tienes, créalo y ponle esto dentro:

**Archivo `requirements.txt`:**
```text
Flask
pymongo
dnspython
