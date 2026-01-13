/* * SCRIPT DE IMPLEMENTACIÓN - PROYECTO INTEGRADOR GRUPO 6
 * Fase 6: Migración y Operaciones CRUD
 */

// 1. SELECCIONAR (O CREAR) LA BASE DE DATOS
use('ProyectoCatequesis_Grupo6');

// (Opcional) Limpiar base de datos previa para evitar duplicados al probar
db.getCollectionNames().forEach(c => db[c].drop());

// 2. CREACIÓN DE COLECCIONES (Validación de Esquema Opcional)
db.createCollection('parroquias');
db.createCollection('usuarios');
db.createCollection('niveles');
db.createCollection('catequistas');
db.createCollection('grupos');
db.createCollection('estudiantes');
db.createCollection('inscripciones');
db.createCollection('asistencias');
db.createCollection('evaluaciones');
db.createCollection('eventos');
db.createCollection('sacramentos');
db.createCollection('certificados');

// 3. INSERCIÓN DE DATOS MIGRADOS (CREATE)
// Estos datos provienen de la salida JSON de SQL Server

// --- Parroquias ---
db.parroquias.insertMany([
  {
    "_id": 1,
    "nombre_parroquia": "Parroquia San Juan",
    "direccion": "Av. Quito 123",
    "telefono": "0991234567",
    "correo": "contacto@parroquia.com"
  },
  {
    "_id": 2,
    "nombre_parroquia": "Parroquia Santa María",
    "direccion": "Calle Olmedo y Venezuela",
    "telefono": "0987654321",
    "correo": "santamaria@parroquia.org"
  }
]);

// --- Estudiantes (Con documentos embebidos) ---
db.estudiantes.insertMany([
  {
    "_id": 1,
    "cedula": "1702345678",
    "nombres": "Ana",
    "apellidos": "Lopez",
    "fecha_nacimiento": new Date("2010-05-15"),
    "direccion": "Av. Los Pinos 45",
    "representante": { "nombre": "Maria Lopez", "telefono": "0998765432" },
    "parroquia": { "id_parroquia": 1, "nombre": "Parroquia San Juan" },
    "certificados": [
        {
            "id_certificado": 1,
            "fecha_emision": new Date("2025-06-01"),
            "sacramento": { "id": 1, "nombre": "Bautismo" },
            "observaciones": "Emitido automáticamente"
        }
    ]
  },
  {
    "_id": 2,
    "cedula": "1758745698",
    "nombres": "Carlos",
    "apellidos": "Pérez",
    "fecha_nacimiento": new Date("2012-05-10"),
    "direccion": "Av. América",
    "representante": { "nombre": "Luis Pérez", "telefono": "0991112223" },
    "parroquia": { "id_parroquia": 1, "nombre": "Parroquia San Juan" },
    "certificados": []
  }
]);

// --- Grupos (Con lista de alumnos) ---
db.grupos.insertMany([
  {
    "_id": 1,
    "nombre_grupo": "Grupo 1",
    "horario": "10:00 - 12:00",
    "dia_reunion": "Sábado",
    "estado": "Activo",
    "parroquia": { "id_parroquia": 1, "nombre": "Parroquia San Juan" },
    "catequista": { "id_catequista": 1, "nombre": "Juan Perez" },
    "nivel": { "id_nivel": 1, "nombre_nivel": "Inicial" },
    "alumnos": [
        { "idEstudiante": 1, "nombre": "Ana Lopez" },
        { "idEstudiante": 2, "nombre": "Carlos Pérez" }
    ]
  }
]);

// --- Inscripciones ---
db.inscripciones.insertMany([
  {
    "_id": 1,
    "fecha_inscripcion": new Date("2025-10-01"),
    "estado": "Activa",
    "estudiante": { "idEstudiante": 1, "nombre": "Ana Lopez" },
    "grupo": { "idGrupo": 1, "nombre_grupo": "Grupo 1" }
  },
  {
    "_id": 2,
    "fecha_inscripcion": new Date("2025-10-01"),
    "estado": "Activa",
    "estudiante": { "idEstudiante": 2, "nombre": "Carlos Pérez" },
    "grupo": { "idGrupo": 1, "nombre_grupo": "Grupo 1" }
  }
]);

// --- Asistencias ---
db.asistencias.insertMany([
  {
    "_id": 1,
    "fecha_sesion": new Date("2025-10-01"),
    "estado": "Presente",
    "inscripcion": { "idInscripcion": 1, "estudiante": "Ana Lopez" }
  },
  {
    "_id": 2,
    "fecha_sesion": new Date("2025-10-01"),
    "estado": "Ausente",
    "inscripcion": { "idInscripcion": 2, "estudiante": "Carlos Pérez" }
  }
]);

// --- Eventos ---
db.eventos.insertMany([
  {
    "_id": 1,
    "nombre_evento": "Retiro de Iniciación",
    "fecha_evento": new Date("2025-08-15"),
    "parroquia": { "id_parroquia": 1, "nombre": "Parroquia San Juan" },
    "participantes": [
        { "id_estudiante": 1, "rol": "Asistente", "nombre_completo": "Ana Lopez" },
        { "id_estudiante": 2, "rol": "Logística", "nombre_completo": "Carlos Pérez" }
    ]
  }
]);

console.log("Migración de datos completada exitosamente.");

// 4. OPERACIONES CRUD DE EJEMPLO (Para cumplir requerimiento)

// A. READ (Leer): Buscar estudiantes de la Parroquia San Juan
const estudiantesSanJuan = db.estudiantes.find({ "parroquia.id_parroquia": 1 });
console.log("Estudiantes encontrados:", estudiantesSanJuan.count());

// B. UPDATE (Actualizar): Cambiar dirección de un estudiante
db.estudiantes.updateOne(
  { "_id": 1 },
  { $set: { "direccion": "Nueva Dirección Av. 10 de Agosto" } }
);

// C. DELETE (Eliminar): Borrar una asistencia errónea
db.asistencias.deleteOne({ "_id": 2 });

// D. AGGREGATION (Lookup): Unir inscripciones con datos completos de estudiantes
db.inscripciones.aggregate([
    {
        $lookup: {
            from: "estudiantes",
            localField: "estudiante.idEstudiante",
            foreignField: "_id",
            as: "datos_completos_estudiante"
        }
    }
]);