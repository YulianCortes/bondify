from sqlalchemy.orm import Session
from backend import models, schemas
from datetime import date # <-- Necesario para el calendario

# 1. Crear sugerencia (Para el familiar) - ACTUALIZADO
def crear_sugerencia(db: Session, actividad: schemas.ActividadCreate):
    nueva_sugerencia = models.Actividad(
        titulo=actividad.titulo,
        descripcion=actividad.descripcion,
        id_familia=actividad.id_familia, 
        es_sugerencia=True,
        aprobada=False,
        fecha=actividad.fecha # <-- INYECCIÓN: Guardamos la fecha si viene del calendario
    )
    db.add(nueva_sugerencia)
    db.commit()
    db.refresh(nueva_sugerencia)
    return nueva_sugerencia

# 2. Aprobar sugerencia (Para el jefe)
def aprobar_y_asignar(db: Session, id_actividad: int, id_asignado: int):
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if actividad:
        actividad.es_sugerencia = False
        actividad.aprobada = True
        actividad.id_usuario_asignado = id_asignado
        db.commit()
    return actividad

# 3. Usuarios y Auth
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

# 4. Crear actividad directamente (Para el jefe) - ACTUALIZADO
def crear_actividad(db: Session, actividad: schemas.ActividadCreate):
    nueva_actividad = models.Actividad(
        titulo=actividad.titulo,
        descripcion=actividad.descripcion,
        id_familia=actividad.id_familia, 
        es_sugerencia=actividad.es_sugerencia,
        aprobada=not actividad.es_sugerencia, # Si no es sugerencia, está aprobada
        fecha=actividad.fecha # <-- INYECCIÓN: Clave para que aparezca el 25 o 27 de abril
    )
    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)
    return nueva_actividad

# 5. Listado de actividades
def obtener_actividades_por_familia(db: Session, id_familia: int):
    # Solo traemos las que NO han terminado para no saturar la vista principal
    return db.query(models.Actividad).filter(
        models.Actividad.id_familia == id_familia,
        models.Actividad.terminada == False 
    ).all()

def obtener_todas_las_actividades(db: Session):
    return db.query(models.Actividad).all()

# 6. Perfil y Disponibilidad
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

# 7. NUEVA SECCIÓN: Lógica para el Calendario Mensual
def obtener_actividades_por_mes(db: Session, id_familia: int, mes: int, anio: int):
    # Filtramos las actividades de una familia que caigan en un mes específico
    from sqlalchemy import extract
    return db.query(models.Actividad).filter(
        models.Actividad.id_familia == id_familia,
        extract('month', models.Actividad.fecha) == mes,
        extract('year', models.Actividad.fecha) == anio
    ).all()

# --- 8. ADICIÓN: LÓGICA DE ASIGNACIONES, PUNTOS Y BORRADO ---

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
    # participaciones es un dict enviado desde el frontend: {id_usuario: bool}
    actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if not actividad:
        return None
    
    familia = db.query(models.Familia).filter(models.Familia.id_familia == actividad.id_familia).first()
    
    for u_id_str, cumplio in participaciones.items():
        u_id = int(u_id_str)
        usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == u_id).first()
        if usuario:
            if cumplio:
                usuario.puntos += 5 # Puntos individuales
                if familia: familia.puntos_familia += 5 # Puntos racha familiar
            else:
                # Penalización a la racha si la actividad se marca como fallida
                if familia: 
                    familia.puntos_familia = max(0, familia.puntos_familia - 5)
    
    actividad.terminada = True
    db.commit()
    return actividad