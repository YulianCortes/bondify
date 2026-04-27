from sqlalchemy.orm import Session
from backend import models, schemas
from datetime import date # <-- Necesario para el calendario
from sqlalchemy import extract

# --- 1. CREAR SUGERENCIA (Para el familiar) ---
def crear_sugerencia(db: Session, actividad: schemas.ActividadCreate):
    nueva_sugerencia = models.Actividad(
        titulo=actividad.titulo,
        descripcion=actividad.descripcion,
        id_familia=actividad.id_familia, 
        es_sugerencia=True,
        aprobada=False,
        fecha=actividad.fecha # Guardamos la fecha si viene del calendario
    )
    db.add(nueva_sugerencia)
    db.commit()
    db.refresh(nueva_sugerencia)
    return nueva_sugerencia

# --- 2. APROBAR SUGERENCIA (Para el jefe) ---
def aprobar_y_asignar(db: Session, id_actividad: int, id_asignado: int):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if actividad:
        actividad.es_sugerencia = False
        actividad.aprobada = True
        actividad.id_usuario_asignado = id_asignado
        db.commit()
    return actividad

# --- 3. USUARIOS Y AUTH ---
def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        telefono=usuario.telefono,
        contrasena=usuario.contrasena,
        tipo_usuario=usuario.tipo_usuario 
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_usuario_by_telefono(db: Session, telefono: str):
    return db.query(models.Usuario).filter(models.Usuario.telefono == telefono).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.correo == email).first()

# --- 4. CREAR ACTIVIDAD DIRECTAMENTE (Para el jefe) ---
def crear_actividad(db: Session, actividad: schemas.ActividadCreate):
    nueva_actividad = models.Actividad(
        titulo=actividad.titulo,
        descripcion=actividad.descripcion,
        id_familia=actividad.id_familia, 
        es_sugerencia=actividad.es_sugerencia,
        aprobada=not actividad.es_sugerencia, 
        fecha=actividad.fecha 
    )
    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)
    return nueva_actividad

# --- 5. LISTADO DE ACTIVIDADES ---
def obtener_actividades_por_familia(db: Session, id_familia: int):
    return db.query(models.Actividad).filter(
        models.Actividad.id_familia == id_familia,
        models.Actividad.terminada == False 
    ).all()

def obtener_todas_las_actividades(db: Session):
    return db.query(models.Actividad).all()

# --- 6. PERFIL Y DISPONIBILIDAD (Recuperado al 100%) ---
def actualizar_disponibilidad(db: Session, usuario_id: int, nueva_disponibilidad: str):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if db_usuario:
        db_usuario.disponibilidad_semanal = nueva_disponibilidad
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

def actualizar_perfil_usuario(db: Session, usuario_id: int, datos_perfil: schemas.UsuarioUpdate):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if db_usuario:
        if datos_perfil.primer_nombre is not None:
            db_usuario.primer_nombre = datos_perfil.primer_nombre
        if datos_perfil.primer_apellido is not None:
            db_usuario.primer_apellido = datos_perfil.primer_apellido
        if datos_perfil.edad is not None:
            db_usuario.edad = datos_perfil.edad
        if datos_perfil.genero is not None:
            db_usuario.genero = datos_perfil.genero
        if datos_perfil.biografia is not None:
            db_usuario.biografia = datos_perfil.biografia
        if datos_perfil.disponibilidad_semanal is not None:
            db_usuario.disponibilidad_semanal = datos_perfil.disponibilidad_semanal
        db.commit()
        db.refresh(db_usuario)
    return db_usuario

# --- 7. LÓGICA PARA EL CALENDARIO MENSUAL ---
def obtener_actividades_por_mes(db: Session, id_familia: int, mes: int, anio: int):
    return db.query(models.Actividad).filter(
        models.Actividad.id_familia == id_familia,
        extract('month', models.Actividad.fecha) == mes,
        extract('year', models.Actividad.fecha) == anio
    ).all()

# --- 8. ASIGNACIONES, PUNTOS Y BORRADO ---
def asignar_usuario_a_actividad(db: Session, id_actividad: int, id_usuario: int):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if actividad and usuario:
        if usuario not in actividad.usuarios_asignados:
            actividad.usuarios_asignados.append(usuario)
            db.commit()
    return actividad

def desasignar_usuario_de_actividad(db: Session, id_actividad: int, id_usuario: int):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if actividad and usuario:
        if usuario in actividad.usuarios_asignados:
            actividad.usuarios_asignados.remove(usuario)
            db.commit()
    return actividad

def eliminar_actividad(db: Session, id_actividad: int):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if actividad:
        db.delete(actividad)
        db.commit()
        return True
    return False

def finalizar_actividad_y_puntos(db: Session, id_actividad: int, participaciones: dict):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if not actividad: return None
    familia = db.query(models.Familia).filter(models.Familia.id_familia == actividad.id_familia).first()
    
    for u_id_str, cumplio in participaciones.items():
        usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == int(u_id_str)).first()
        if usuario:
            if cumplio:
                usuario.puntos += 5 
                if familia: familia.puntos_familia += 5 
            else:
                if familia: familia.puntos_familia = max(0, familia.puntos_familia - 5)
    
    actividad.terminada = True
    db.commit()
    return actividad

# --- 9. MURO FAMILIAR ---
def crear_mensaje_muro(db: Session, id_familia: int, mensaje: schemas.MuroCreate):
    hoy_str = date.today().isoformat()
    nuevo_mensaje = models.MuroMensaje(
        id_familia=id_familia,
        autor=mensaje.autor,
        contenido=mensaje.contenido,
        tipo=mensaje.tipo,
        fecha=hoy_str
    )
    db.add(nuevo_mensaje)
    db.commit()
    db.refresh(nuevo_mensaje)
    return nuevo_mensaje

def obtener_mensajes_muro_hoy(db: Session, id_familia: int):
    hoy_str = date.today().isoformat()
    return db.query(models.MuroMensaje).filter(
        models.MuroMensaje.id_familia == id_familia,
        models.MuroMensaje.fecha == hoy_str
    ).all()

# --- 10. ADICIÓN: DISOLVER FAMILIA (TU IDEA DE DESVINCULAR) ---
def disolver_familia_completo(db: Session, id_familia: int, id_jefe: int):
    familia = db.query(models.Familia).filter(
        models.Familia.id_familia == id_familia, 
        models.Familia.id_jefe == id_jefe
    ).first()
    
    if not familia:
        return False

    try:
        # DESVINCULACIÓN: Ponemos el id_familia de los miembros en NULL
        db.query(models.Usuario).filter(models.Usuario.id_familia == id_familia).update(
            {models.Usuario.id_familia: None}, 
            synchronize_session="fetch"
        )
        
        # ELIMINACIÓN EN CASCADA: MySQL borrará actividades y mensajes por el models.py
        db.delete(familia)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error en la cirugía de disolución: {e}")
        return False