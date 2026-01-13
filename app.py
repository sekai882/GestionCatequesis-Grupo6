from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_grupo6'

# --- CONEXIÓN A MONGODB ATLAS ---
MONGO_URI = "mongodb+srv://UserJosue:josuemullo10@clusterudla01.foq4q8w.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client['ProyectoCatequesis_Grupo6']

# --- DEFINICIÓN DE COLECCIONES ---
collection_estudiantes = db['estudiantes']
collection_grupos = db['grupos']
collection_parroquias = db['parroquias']
collection_catequistas = db['catequistas']
collection_niveles = db['niveles']
collection_inscripciones = db['inscripciones']
collection_asistencias = db['asistencias']

# ==========================================
# RUTA DE INICIO
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# MÓDULO 1: ESTUDIANTES
# ==========================================

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        cedula = request.form['cedula']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        
        nuevo_estudiante = {
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "parroquia": {"id_parroquia": 1, "nombre": "San Juan"},
            "certificados": []
        }
        
        try:
            collection_estudiantes.insert_one(nuevo_estudiante)
            flash('¡Estudiante registrado correctamente!', 'success')
            return redirect(url_for('consultas'))
        except DuplicateKeyError:
            flash(f'Error: La cédula {cedula} ya existe.', 'danger')
            return redirect(url_for('registrar'))
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')
            return redirect(url_for('registrar'))
    
    return render_template('registro.html')

@app.route('/consultas')
def consultas():
    estudiantes = collection_estudiantes.find()
    return render_template('consultas.html', estudiantes=estudiantes)

@app.route('/editar/<string:id_estudiante>', methods=['GET', 'POST'])
def editar(id_estudiante):
    try: id_obj = ObjectId(id_estudiante)
    except: id_obj = int(id_estudiante)
        
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        direccion = request.form['direccion']
        try:
            collection_estudiantes.update_one(
                {'_id': id_obj},
                {'$set': {'nombres': nombres, 'apellidos': apellidos, 'direccion': direccion}}
            )
            flash('Datos actualizados correctamente.', 'success')
            return redirect(url_for('consultas'))
        except Exception as e:
            flash(f'Error al actualizar: {str(e)}', 'danger')
            return redirect(url_for('consultas'))

    estudiante = collection_estudiantes.find_one({'_id': id_obj})
    return render_template('editar_estudiante.html', estudiante=estudiante)

@app.route('/eliminar/<string:id_estudiante>')
def eliminar(id_estudiante):
    try:
        try: collection_estudiantes.delete_one({'_id': ObjectId(id_estudiante)})
        except: collection_estudiantes.delete_one({'_id': int(id_estudiante)})
        flash('Estudiante eliminado correctamente.', 'warning')
    except Exception as e:
        flash(f'Error al eliminar: {str(e)}', 'danger')
    return redirect(url_for('consultas'))


# ==========================================
# MÓDULO 2: GRUPOS
# ==========================================

@app.route('/grupos')
def listar_grupos():
    grupos = collection_grupos.find()
    return render_template('grupos.html', grupos=grupos)

@app.route('/crear_grupo', methods=['GET'])
def form_grupo():
    parroquias = collection_parroquias.find()
    catequistas = collection_catequistas.find()
    niveles = collection_niveles.find()
    return render_template('form_grupo.html', parroquias=parroquias, catequistas=catequistas, niveles=niveles)

@app.route('/guardar_grupo', methods=['POST'])
def guardar_grupo():
    try:
        nombre_grupo = request.form['nombre_grupo']
        horario = request.form['horario']
        dia = request.form['dia']
        
        id_parroquia = int(request.form['parroquia'])
        id_catequista = int(request.form['catequista'])
        id_nivel = int(request.form['nivel'])
        
        parroquia_obj = collection_parroquias.find_one({'_id': id_parroquia})
        catequista_obj = collection_catequistas.find_one({'_id': id_catequista})
        nivel_obj = collection_niveles.find_one({'_id': id_nivel})
        
        nuevo_grupo = {
            "nombre_grupo": nombre_grupo,
            "horario": horario,
            "dia_reunion": dia,
            "estado": "Activo",
            "parroquia": {"id_parroquia": parroquia_obj['_id'], "nombre": parroquia_obj['nombre_parroquia']},
            "catequista": {"id_catequista": catequista_obj['_id'], "nombre": f"{catequista_obj['nombres']} {catequista_obj['apellidos']}"},
            "nivel": {"id_nivel": nivel_obj['_id'], "nombre_nivel": nivel_obj['nombre_nivel']},
            "alumnos": []
        }
        
        collection_grupos.insert_one(nuevo_grupo)
        flash('Grupo creado exitosamente', 'success')
        return redirect(url_for('listar_grupos'))
    except Exception as e:
        flash(f'Error al crear grupo: {str(e)}', 'danger')
        return redirect(url_for('form_grupo'))

# NUEVO: ELIMINAR GRUPO
@app.route('/eliminar_grupo/<string:id_grupo>')
def eliminar_grupo(id_grupo):
    try:
        try: id_obj = ObjectId(id_grupo)
        except: id_obj = int(id_grupo)
        
        collection_grupos.delete_one({'_id': id_obj})
        flash('Grupo eliminado correctamente.', 'warning')
    except Exception as e:
        flash(f'Error al eliminar grupo: {str(e)}', 'danger')
    return redirect(url_for('listar_grupos'))

# ==========================================
# MÓDULO 3: INSCRIPCIONES
# ==========================================

@app.route('/inscripciones')
def listar_inscripciones():
    inscripciones = collection_inscripciones.find()
    return render_template('inscripciones.html', inscripciones=inscripciones)

@app.route('/nueva_inscripcion', methods=['GET'])
def form_inscripcion():
    estudiantes = collection_estudiantes.find()
    grupos = collection_grupos.find()
    return render_template('form_inscripcion.html', estudiantes=estudiantes, grupos=grupos)

@app.route('/guardar_inscripcion', methods=['POST'])
def guardar_inscripcion():
    try:
        id_estudiante_str = request.form['estudiante']
        id_grupo_str = request.form['grupo']
        
        try: id_est_obj = ObjectId(id_estudiante_str)
        except: id_est_obj = int(id_estudiante_str)

        try: id_grp_obj = ObjectId(id_grupo_str)
        except: id_grp_obj = int(id_grupo_str)

        estudiante = collection_estudiantes.find_one({'_id': id_est_obj})
        grupo = collection_grupos.find_one({'_id': id_grp_obj})
        
        if not estudiante or not grupo:
            flash('Error: Datos no encontrados', 'danger')
            return redirect(url_for('form_inscripcion'))

        nueva_inscripcion = {
            "fecha_inscripcion": datetime.datetime.now(),
            "estado": "Activa",
            "estudiante": {"idEstudiante": estudiante['_id'], "nombre": f"{estudiante['nombres']} {estudiante['apellidos']}"},
            "grupo": {"idGrupo": grupo['_id'], "nombre_grupo": grupo['nombre_grupo']}
        }
        collection_inscripciones.insert_one(nueva_inscripcion)

        # Actualizar lista de alumnos en el grupo
        alumno_para_grupo = {"idEstudiante": estudiante['_id'], "nombre": f"{estudiante['nombres']} {estudiante['apellidos']}"}
        collection_grupos.update_one({'_id': grupo['_id']}, {'$push': {'alumnos': alumno_para_grupo}})

        flash('Inscripción realizada con éxito.', 'success')
        return redirect(url_for('listar_inscripciones'))
    except Exception as e:
        flash(f'Error al inscribir: {str(e)}', 'danger')
        return redirect(url_for('form_inscripcion'))

# NUEVO: ELIMINAR INSCRIPCIÓN (Y SACAR DEL GRUPO)
@app.route('/eliminar_inscripcion/<string:id_inscripcion>')
def eliminar_inscripcion(id_inscripcion):
    try:
        try: id_ins_obj = ObjectId(id_inscripcion)
        except: id_ins_obj = int(id_inscripcion)
        
        # 1. Buscar la inscripción para saber a qué grupo y estudiante pertenece
        inscripcion = collection_inscripciones.find_one({'_id': id_ins_obj})
        
        if inscripcion:
            id_grupo = inscripcion['grupo']['idGrupo']
            id_estudiante = inscripcion['estudiante']['idEstudiante']
            
            # 2. Eliminar al estudiante del Array 'alumnos' en el Grupo (DESNORMALIZACIÓN INVERSA)
            # Usamos $pull para sacar el elemento que coincida con el ID del estudiante
            collection_grupos.update_one(
                {'_id': id_grupo},
                {'$pull': {'alumnos': {'idEstudiante': id_estudiante}}}
            )
            
            # 3. Eliminar el documento de inscripción
            collection_inscripciones.delete_one({'_id': id_ins_obj})
            flash('Inscripción eliminada y lista del grupo actualizada.', 'warning')
        else:
            flash('Inscripción no encontrada.', 'danger')
            
    except Exception as e:
        flash(f'Error al eliminar inscripción: {str(e)}', 'danger')
    return redirect(url_for('listar_inscripciones'))

# ==========================================
# MÓDULO 4: ASISTENCIAS
# ==========================================

@app.route('/asistencia/seleccionar_grupo')
def asistencia_seleccionar_grupo():
    grupos = collection_grupos.find()
    return render_template('asistencia_grupos.html', grupos=grupos)

@app.route('/asistencia/tomar/<string:id_grupo>', methods=['GET'])
def tomar_asistencia_form(id_grupo):
    try: id_obj = ObjectId(id_grupo)
    except: id_obj = int(id_grupo)
    grupo = collection_grupos.find_one({'_id': id_obj})
    inscripciones = list(collection_inscripciones.find({
        '$or': [{'grupo.idGrupo': id_obj}, {'grupo.idGrupo': str(id_obj)}]
    }))
    return render_template('asistencia_tomar.html', grupo=grupo, inscripciones=inscripciones, fecha_hoy=datetime.date.today())

@app.route('/guardar_asistencia', methods=['POST'])
def guardar_asistencia():
    try:
        fecha_str = request.form['fecha']
        observacion_general = request.form['observacion']
        id_inscripciones = request.form.getlist('id_inscripcion')
        registros_insertar = []
        
        for id_ins in id_inscripciones:
            estado = request.form.get(f'estado_{id_ins}') 
            nombre_est = request.form.get(f'nombre_{id_ins}')
            try: id_ins_obj = ObjectId(id_ins)
            except: id_ins_obj = int(id_ins)

            registro = {
                "fecha_sesion": datetime.datetime.strptime(fecha_str, '%Y-%m-%d'),
                "estado": estado,
                "inscripcion": {"idInscripcion": id_ins_obj, "estudiante": nombre_est},
                "observacion": observacion_general
            }
            registros_insertar.append(registro)
            
        if registros_insertar:
            collection_asistencias.insert_many(registros_insertar)
            flash(f'Se guardó la asistencia de {len(registros_insertar)} estudiantes.', 'success')
        
        return redirect(url_for('ver_asistencias'))
    except Exception as e:
        flash(f'Error al guardar: {str(e)}', 'danger')
        return redirect(url_for('asistencia_seleccionar_grupo'))

@app.route('/ver_asistencias')
def ver_asistencias():
    asistencias = collection_asistencias.find().sort('fecha_sesion', -1).limit(50)
    return render_template('asistencia_listado.html', asistencias=asistencias)

# NUEVO: ELIMINAR ASISTENCIA
@app.route('/eliminar_asistencia/<string:id_asistencia>')
def eliminar_asistencia(id_asistencia):
    try:
        try: id_obj = ObjectId(id_asistencia)
        except: id_obj = int(id_asistencia)
        
        collection_asistencias.delete_one({'_id': id_obj})
        flash('Registro de asistencia eliminado.', 'warning')
    except Exception as e:
        flash(f'Error al eliminar asistencia: {str(e)}', 'danger')
    return redirect(url_for('ver_asistencias'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)