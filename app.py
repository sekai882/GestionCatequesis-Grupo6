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

# --- COLECCIONES ---
collection_estudiantes = db['estudiantes']
collection_grupos = db['grupos']
collection_parroquias = db['parroquias']
collection_catequistas = db['catequistas']
collection_niveles = db['niveles']
collection_inscripciones = db['inscripciones']
collection_asistencias = db['asistencias']
# Nuevas colecciones
collection_evaluaciones = db['evaluaciones']
collection_certificados = db['certificados']
collection_sacramentos = db['sacramentos']

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
        nuevo_estudiante = {
            "cedula": cedula,
            "nombres": request.form['nombres'],
            "apellidos": request.form['apellidos'],
            "fecha_nacimiento": request.form['fecha_nacimiento'], # Guardamos string o date
            "representante": {
                "nombre": request.form.get('nombre_rep', ''),
                "telefono": request.form.get('telefono_rep', '')
            },
            "parroquia": {"id_parroquia": 1, "nombre": "San Juan"}
        }
        try:
            collection_estudiantes.insert_one(nuevo_estudiante)
            flash('¡Estudiante registrado correctamente!', 'success')
            return redirect(url_for('consultas'))
        except DuplicateKeyError:
            flash(f'Error: La cédula {cedula} ya existe.', 'danger')
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
        try:
            collection_estudiantes.update_one(
                {'_id': id_obj},
                {'$set': {
                    'nombres': request.form['nombres'],
                    'apellidos': request.form['apellidos'],
                    'representante.nombre': request.form.get('nombre_rep'),
                    'representante.telefono': request.form.get('telefono_rep')
                }}
            )
            flash('Datos actualizados.', 'success')
            return redirect(url_for('consultas'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    estudiante = collection_estudiantes.find_one({'_id': id_obj})
    return render_template('editar_estudiante.html', estudiante=estudiante)

@app.route('/eliminar/<string:id_estudiante>')
def eliminar(id_estudiante):
    try:
        try: collection_estudiantes.delete_one({'_id': ObjectId(id_estudiante)})
        except: collection_estudiantes.delete_one({'_id': int(id_estudiante)})
        flash('Estudiante eliminado.', 'warning')
    except: pass
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
        # Recuperamos objetos completos para referencia extendida
        cat_obj = collection_catequistas.find_one({'_id': int(request.form['catequista'])})
        parr_obj = collection_parroquias.find_one({'_id': int(request.form['parroquia'])})
        niv_obj = collection_niveles.find_one({'_id': int(request.form['nivel'])})

        nuevo_grupo = {
            "nombre_grupo": request.form['nombre_grupo'],
            "horario": request.form['horario'],
            "dia_reunion": request.form['dia'],
            "estado": "Activo",
            "parroquia": {"id": parr_obj['_id'], "nombre": parr_obj['nombre_parroquia']},
            "catequista": {"id": cat_obj['_id'], "nombre": f"{cat_obj['nombres']} {cat_obj['apellidos']}"},
            "nivel": {"id_nivel": niv_obj['_id'], "nombre_nivel": niv_obj['nombre_nivel']},
            "alumnos": []
        }
        collection_grupos.insert_one(nuevo_grupo)
        flash('Grupo creado.', 'success')
        return redirect(url_for('listar_grupos'))
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('form_grupo'))

@app.route('/eliminar_grupo/<string:id_grupo>')
def eliminar_grupo(id_grupo):
    try:
        try: id_obj = ObjectId(id_grupo)
        except: id_obj = int(id_grupo)
        collection_grupos.delete_one({'_id': id_obj})
        flash('Grupo eliminado.', 'warning')
    except: pass
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
        try: id_est = ObjectId(request.form['estudiante'])
        except: id_est = int(request.form['estudiante'])
        try: id_grp = ObjectId(request.form['grupo'])
        except: id_grp = int(request.form['grupo'])

        est = collection_estudiantes.find_one({'_id': id_est})
        grp = collection_grupos.find_one({'_id': id_grp})

        nueva_inscripcion = {
            "fecha_inscripcion": datetime.datetime.now(),
            "estado": "Activa",
            "estudiante": {"idEstudiante": est['_id'], "nombre": f"{est['nombres']} {est['apellidos']}"},
            "grupo": {"idGrupo": grp['_id'], "nombre_grupo": grp['nombre_grupo']}
        }
        collection_inscripciones.insert_one(nueva_inscripcion)
        
        # Desnormalización: Agregar a lista de alumnos del grupo
        alumno_data = {"idEstudiante": est['_id'], "nombre": f"{est['nombres']} {est['apellidos']}"}
        collection_grupos.update_one({'_id': grp['_id']}, {'$push': {'alumnos': alumno_data}})
        
        flash('Inscripción exitosa.', 'success')
        return redirect(url_for('listar_inscripciones'))
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('form_inscripcion'))

@app.route('/eliminar_inscripcion/<string:id_inscripcion>')
def eliminar_inscripcion(id_inscripcion):
    try:
        try: id_obj = ObjectId(id_inscripcion)
        except: id_obj = int(id_inscripcion)
        
        ins = collection_inscripciones.find_one({'_id': id_obj})
        if ins:
            # Sacar del grupo
            collection_grupos.update_one(
                {'_id': ins['grupo']['idGrupo']},
                {'$pull': {'alumnos': {'idEstudiante': ins['estudiante']['idEstudiante']}}}
            )
            collection_inscripciones.delete_one({'_id': id_obj})
            flash('Inscripción eliminada.', 'warning')
    except: pass
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
    # Buscar inscripciones por ID de grupo (string o int)
    inscripciones = list(collection_inscripciones.find({
        '$or': [{'grupo.idGrupo': id_obj}, {'grupo.idGrupo': str(id_obj)}]
    }))
    return render_template('asistencia_tomar.html', grupo=grupo, inscripciones=inscripciones, fecha_hoy=datetime.date.today())

@app.route('/guardar_asistencia', methods=['POST'])
def guardar_asistencia():
    try:
        fecha = datetime.datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        ids = request.form.getlist('id_inscripcion')
        
        lista_insertar = []
        for id_ins in ids:
            try: id_ins_obj = ObjectId(id_ins)
            except: id_ins_obj = int(id_ins)
            
            estado = request.form.get(f'estado_{id_ins}')
            nombre = request.form.get(f'nombre_{id_ins}')
            
            lista_insertar.append({
                "fecha_sesion": fecha,
                "estado": estado,
                "inscripcion": {"idInscripcion": id_ins_obj, "estudiante": nombre},
                "observacion": request.form['observacion']
            })
            
        if lista_insertar:
            collection_asistencias.insert_many(lista_insertar)
            flash(f'Asistencia guardada ({len(lista_insertar)}).', 'success')
        return redirect(url_for('ver_asistencias'))
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('asistencia_seleccionar_grupo'))

@app.route('/ver_asistencias')
def ver_asistencias():
    asistencias = collection_asistencias.find().sort('fecha_sesion', -1).limit(50)
    return render_template('asistencia_listado.html', asistencias=asistencias)

# ==========================================
# MÓDULO 5: CATEQUISTAS (NUEVO)
# ==========================================
@app.route('/catequistas')
def listar_catequistas():
    # En Mongo, los catequistas tienen ID numérico según tu migración
    catequistas = collection_catequistas.find()
    return render_template('catequistas.html', catequistas=catequistas)

@app.route('/registrar_catequista', methods=['GET', 'POST'])
def registrar_catequista():
    if request.method == 'POST':
        # Generar un ID simple manual (max + 1) o usar ObjectId
        last = collection_catequistas.find_one(sort=[("_id", -1)])
        new_id = (last['_id'] + 1) if last and isinstance(last['_id'], int) else 100
        
        nuevo_cat = {
            "_id": new_id, # Mantenemos IDs enteros para compatibilidad con migración
            "nombre": request.form['nombre'],
            "apellido": request.form['apellido'],
            "cedula": request.form['cedula'],
            "telefono": request.form['telefono'],
            "correo": request.form['correo']
        }
        collection_catequistas.insert_one(nuevo_cat)
        flash('Catequista registrado.', 'success')
        return redirect(url_for('listar_catequistas'))
    return render_template('form_catequista.html')

# ==========================================
# MÓDULO 6: EVALUACIONES Y PROMOCIÓN (LOGIC)
# ==========================================
@app.route('/evaluar', methods=['GET', 'POST'])
def evaluar_estudiante():
    if request.method == 'POST':
        try:
            try: id_ins = ObjectId(request.form['inscripcion'])
            except: id_ins = int(request.form['inscripcion'])
            
            nota = float(request.form['calificacion'])
            
            # 1. Guardar la evaluación
            evaluacion = {
                "fecha": datetime.datetime.now(),
                "inscripcion_id": id_ins,
                "calificacion": nota,
                "observacion": request.form['observacion']
            }
            collection_evaluaciones.insert_one(evaluacion)
            
            # 2. LÓGICA DE TRIGGER: Promoción automática si nota >= 7
            if nota >= 7.0:
                # Buscamos la inscripción actual
                ins = collection_inscripciones.find_one({'_id': id_ins})
                if ins:
                    grupo_actual = collection_grupos.find_one({'_id': ins['grupo']['idGrupo']})
                    nivel_actual_id = grupo_actual['nivel']['id_nivel']
                    
                    # Buscar el siguiente nivel (Suponemos IDs secuenciales: 1->2->3)
                    siguiente_nivel_id = nivel_actual_id + 1
                    
                    # Buscar un grupo que tenga ese nivel
                    nuevo_grupo = collection_grupos.find_one({'nivel.id_nivel': siguiente_nivel_id})
                    
                    if nuevo_grupo:
                        # ACTUALIZAR INSCRIPCIÓN (CAMBIAR DE GRUPO)
                        collection_inscripciones.update_one(
                            {'_id': id_ins},
                            {'$set': {'grupo': {'idGrupo': nuevo_grupo['_id'], 'nombre_grupo': nuevo_grupo['nombre_grupo']}}}
                        )
                        # ACTUALIZAR ARRAYS DE GRUPOS (Sacar de uno, poner en otro)
                        collection_grupos.update_one({'_id': grupo_actual['_id']}, 
                                                     {'$pull': {'alumnos': {'idEstudiante': ins['estudiante']['idEstudiante']}}})
                        collection_grupos.update_one({'_id': nuevo_grupo['_id']}, 
                                                     {'$push': {'alumnos': {'idEstudiante': ins['estudiante']['idEstudiante'], 'nombre': ins['estudiante']['nombre']}}})
                        
                        flash(f'Nota {nota}: ¡Estudiante promovido automáticamente al nivel {nuevo_grupo["nivel"]["nombre_nivel"]}!', 'success')
                    else:
                        flash(f'Nota {nota}: Aprobado, pero no hay grupos disponibles para el siguiente nivel.', 'warning')
            else:
                flash(f'Nota {nota}: Registrada. No alcanza puntaje para promoción.', 'info')
                
            return redirect(url_for('consultas'))
            
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    # GET: Listar inscripciones activas
    inscripciones = collection_inscripciones.find({'estado': 'Activa'})
    return render_template('form_evaluacion.html', inscripciones=inscripciones)

@app.route('/ver_notas')
def ver_notas():
    # Pipeline de agregación para unir datos (Lookup simulado o datos directos)
    notas = list(collection_evaluaciones.find().sort('fecha', -1))
    # Enriquecer datos manualmente (NoSQL way)
    for n in notas:
        ins = collection_inscripciones.find_one({'_id': n['inscripcion_id']})
        if ins:
            n['alumno'] = ins['estudiante']['nombre']
            n['grupo'] = ins['grupo']['nombre_grupo']
    return render_template('notas.html', notas=notas)

# ==========================================
# MÓDULO 7: CERTIFICADOS
# ==========================================
@app.route('/certificados')
def listar_certificados():
    certificados = collection_certificados.find().sort('fechaEmision', -1)
    return render_template('certificados.html', certificados=certificados)

@app.route('/generar_certificado', methods=['GET', 'POST'])
def generar_certificado():
    if request.method == 'POST':
        try: id_est = ObjectId(request.form['estudiante'])
        except: id_est = int(request.form['estudiante'])
        
        est = collection_estudiantes.find_one({'_id': id_est})
        sac = request.form['sacramento']
        
        cert = {
            "fechaEmision": datetime.datetime.now(),
            "estudiante": est['nombres'] + " " + est['apellidos'],
            "sacramento": sac,
            "observacion": "Emitido digitalmente"
        }
        collection_certificados.insert_one(cert)
        flash('Certificado generado.', 'success')
        return redirect(url_for('listar_certificados'))

    estudiantes = collection_estudiantes.find()
    return render_template('form_certificado.html', estudiantes=estudiantes)

if __name__ == '__main__':
    app.run(debug=True, port=5001)