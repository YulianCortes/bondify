from fastapi import FastAPI, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from backend import crud, models, schemas
from backend.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from datetime import date # AGREGADO PARA EL MURO

# 1. Conexión y creación de tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bondify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- RUTAS DE USUARIO ---

@app.post("/usuarios/", response_model=schemas.Usuario)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, email=usuario.correo)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return crud.crear_usuario(db=db, usuario=usuario)

@app.post("/login/")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    user = None
    if usuario.correo:
        user = crud.get_usuario_by_email(db, usuario.correo)
    elif usuario.telefono:
        user = crud.get_usuario_by_telefono(db, usuario.telefono)
    
    if not user or user.contrasena != usuario.contrasena:
        raise HTTPException(status_code=400, detail="Datos incorrectos")
    
    return {
        "mensaje": "Inicio de sesión exitoso", 
        "usuario": user.nombre, 
        "rol": user.tipo_usuario,
        "id_usuario": user.id_usuario,
        "puntos": user.puntos 
    }

@app.put("/usuarios/{usuario_id}/perfil")
def actualizar_perfil(usuario_id: int, perfil: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario_actualizado = crud.actualizar_perfil_usuario(db, usuario_id, perfil)
    if usuario_actualizado is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_actualizado

@app.get("/usuarios/{usuario_id}/perfil")
def obtener_perfil(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# --- GESTIÓN DE FAMILIA ---

@app.post("/familias/", response_model=schemas.FamiliaResponse)
def crear_familia(familia: schemas.FamiliaCreate, db: Session = Depends(get_db)):
    nueva_familia = models.Familia(nombre_familia=familia.nombre_familia, id_jefe=familia.id_jefe)
    db.add(nueva_familia)
    db.commit()
    db.refresh(nueva_familia)
    jefe = db.query(models.Usuario).filter(models.Usuario.id_usuario == familia.id_jefe).first()
    if jefe:
        jefe.id_familia = nueva_familia.id_familia
        db.commit()
    return nueva_familia

@app.get("/familias/{usuario_id}/integrantes")
def listar_integrantes(usuario_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if not user or not user.id_familia:
        return {"mensaje": "Sin familia", "integrantes": [], "nombre_familia": "N/A", "puntos_familia": 0}
    
    fam = db.query(models.Familia).filter(models.Familia.id_familia == user.id_familia).first()
    miembros = db.query(models.Usuario).filter(models.Usuario.id_familia == user.id_familia).all()
    
    return {
        "nombre_familia": fam.nombre_familia,
        "id_familia": fam.id_familia,
        "id_jefe": fam.id_jefe,
        "puntos_familia": fam.puntos_familia,
        "integrantes": [
            {
                "id_usuario": m.id_usuario, 
                "nombre": m.nombre, 
                "rol": m.tipo_usuario,
                "puntos": m.puntos,
                "disponibilidad": m.disponibilidad_semanal 
            } for m in miembros
        ]
    }

@app.post("/familias/miembros/")
def agregar_miembro(correo: str, id_jefe: int, db: Session = Depends(get_db)):
    jefe = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_jefe).first()
    if not jefe or not jefe.id_familia:
        raise HTTPException(status_code=400, detail="Debes crear una familia primero")
    nuevo_miembro = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not nuevo_miembro:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    nuevo_miembro.id_familia = jefe.id_familia
    db.commit()
    return {"mensaje": f"¡{nuevo_miembro.nombre} añadido!"}

@app.delete("/familias/miembros/{usuario_id_a_borrar}")
def borrar_miembro(usuario_id_a_borrar: int, id_jefe: int = Query(...), db: Session = Depends(get_db)):
    familia = db.query(models.Familia).filter(models.Familia.id_jefe == id_jefe).first()
    if not familia:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    target = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_id_a_borrar, 
        models.Usuario.id_familia == familia.id_familia
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="No encontrado")
    target.id_familia = None
    db.commit()
    return {"mensaje": "Miembro removido"}

# --- CIRUGÍA: RUTA DE DISOLVER ACTUALIZADA (ORDEN DE LIMPIEZA TOTAL) ---
@app.delete("/familias/disolver/{id_familia}")
def disolver_familia(id_familia: int, id_jefe: int, db: Session = Depends(get_db)):
    print(f"SISTEMA: Intento de disolución - Familia: {id_familia} por Jefe: {id_jefe}")
    
    familia = db.query(models.Familia).filter(
        models.Familia.id_familia == id_familia, 
        models.Familia.id_jefe == id_jefe
    ).first()
    
    if not familia:
        print("SISTEMA: Error - No se encontró la familia o no es el jefe real.")
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    try:
        # 1. Desvincular usuarios (Ponemos su id_familia en NULL)
        db.query(models.Usuario).filter(models.Usuario.id_familia == id_familia).update({"id_familia": None})
        
        # 2. Borrar mensajes del muro vinculados
        db.query(models.MuroMensaje).filter(models.MuroMensaje.id_familia == id_familia).delete()
        
        # 3. Borrar actividades vinculadas
        db.query(models.Actividad).filter(models.Actividad.id_familia == id_familia).delete()
        
        # 4. Ahora sí, borrar la familia del registro
        db.delete(familia)
        db.commit()
        print(f"SISTEMA: ¡Familia {id_familia} disuelta con éxito!")
        return {"mensaje": "Grupo familiar disuelto correctamente."}
    except Exception as e:
        db.rollback()
        print(f"SISTEMA: Error crítico al disolver -> {e}")
        raise HTTPException(status_code=500, detail="Error de integridad en la base de datos")

# --- RUTAS DE ACTIVIDADES ---

@app.post("/actividades/", response_model=schemas.ActividadResponse)
def crear_actividad(actividad: schemas.ActividadCreate, db: Session = Depends(get_db)):
    return crud.crear_actividad(db=db, actividad=actividad)

@app.get("/familias/{id_familia}/actividades")
def listar_actividades(id_familia: int, db: Session = Depends(get_db)):
    actividades = db.query(models.Actividad).filter(
        models.Actividad.id_familia == id_familia,
        models.Actividad.terminada == False
    ).all()
    resultado = []
    for a in actividades:
        resultado.append({
            "id_actividad": a.id_actividad,
            "titulo": a.titulo,
            "descripcion": a.descripcion,
            "es_sugerencia": a.es_sugerencia,
            "terminada": a.terminada,
            "fecha": a.fecha, 
            "usuarios_asignados": [{"id_usuario": u.id_usuario, "nombre": u.nombre} for u in a.usuarios_asignados]
        })
    return resultado

@app.get("/familias/{id_familia}/actividades/mes/{mes}/{anio}")
def obtener_calendario_mensual(id_familia: int, mes: int, anio: int, db: Session = Depends(get_db)):
    return crud.obtener_actividades_por_mes(db, id_familia, mes, anio)

@app.put("/actividades/{id_actividad}/finalizar")
def finalizar_actividad(id_actividad: int, participaciones: Dict[str, bool] = Body(...), db: Session = Depends(get_db)):
    act = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if not act: raise HTTPException(status_code=404)
    fam = db.query(models.Familia).filter(models.Familia.id_familia == act.id_familia).first()
    
    actividad_exitosa = any(participaciones.values())
    
    for uid_str, cumplio in participaciones.items():
        user = db.query(models.Usuario).filter(models.Usuario.id_usuario == int(uid_str)).first()
        if user:
            if cumplio:
                user.puntos += 5 
            else:
                user.puntos -= 5 

    if actividad_exitosa:
        fam.puntos_familia += 1 
    else:
        fam.puntos_familia -= 1 

    if fam.puntos_familia < 0: fam.puntos_familia = 0
    act.terminada = True
    db.commit()
    return {"mensaje": "Puntos procesados", "puntos_familia": fam.puntos_familia}

@app.put("/actividades/{id_actividad}/asignar/{id_usuario}")
def asignar_miembro(id_actividad: int, id_usuario: int, db: Session = Depends(get_db)):
    existe = db.query(models.AsignacionActividad).filter(
        models.AsignacionActividad.id_actividad == id_actividad,
        models.AsignacionActividad.id_usuario == id_usuario
    ).first()
    if not existe:
        db.add(models.AsignacionActividad(id_actividad=id_actividad, id_usuario=id_usuario))
        db.commit()
    return {"mensaje": "Asignado"}

@app.delete("/actividades/{id_actividad}/desasignar/{id_usuario}")
def desasignar_miembro(id_actividad: int, id_usuario: int, db: Session = Depends(get_db)):
    db.query(models.AsignacionActividad).filter(
        models.AsignacionActividad.id_actividad == id_actividad,
        models.AsignacionActividad.id_usuario == id_usuario
    ).delete()
    db.commit()
    return {"mensaje": "Removido"}

@app.delete("/actividades/{id_actividad}")
def borrar_actividad(id_actividad: int, db: Session = Depends(get_db)):
    act = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if not act: raise HTTPException(status_code=404)
    db.delete(act)
    db.commit()
    return {"mensaje": "Eliminada"}

# --- RUTAS DEL MURO FAMILIAR ---

@app.post("/familias/{id_familia}/muro", response_model=schemas.MuroResponse)
def publicar_mensaje_muro(id_familia: int, mensaje: schemas.MuroCreate, db: Session = Depends(get_db)):
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

@app.get("/familias/{id_familia}/muro", response_model=List[schemas.MuroResponse])
def obtener_mensajes_muro_hoy(id_familia: int, db: Session = Depends(get_db)):
    hoy_str = date.today().isoformat()
    mensajes = db.query(models.MuroMensaje).filter(
        models.MuroMensaje.id_familia == id_familia,
        models.MuroMensaje.fecha == hoy_str
    ).all()
    
    return mensajes