from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import crud, models, schemas
from backend.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

# Creamos las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bondify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Función para conectar con la base de datos
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
        "id_usuario": user.id_usuario 
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

# 1. Crear la familia (Solo el Jefe)
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

# 2. Listar integrantes
@app.get("/familias/{usuario_id}/integrantes")
def listar_integrantes(usuario_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    
    if not user or not user.id_familia:
        return {"mensaje": "Sin familia", "integrantes": [], "nombre_familia": "N/A", "id_jefe": None}
    
    fam = db.query(models.Familia).filter(models.Familia.id_familia == user.id_familia).first()
    miembros = db.query(models.Usuario).filter(models.Usuario.id_familia == user.id_familia).all()
    
    return {
        "nombre_familia": fam.nombre_familia,
        "id_familia": fam.id_familia,
        "id_jefe": fam.id_jefe,
        "integrantes": [
            {
                "id_usuario": m.id_usuario, 
                "nombre": m.nombre, 
                "primer_nombre": m.primer_nombre,
                "rol": m.tipo_usuario
            } for m in miembros
        ]
    }

# 3. Agregar miembro por correo
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

# 4. Borrar integrante individual
@app.delete("/familias/miembros/{usuario_id_a_borrar}")
def borrar_miembro(usuario_id_a_borrar: int, id_jefe: int, db: Session = Depends(get_db)):
    familia = db.query(models.Familia).filter(models.Familia.id_jefe == id_jefe).first()
    if not familia:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    target = db.query(models.Usuario).filter(
        models.Usuario.id_usuario == usuario_id_a_borrar, 
        models.Usuario.id_familia == familia.id_familia
    ).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en la familia")
    
    target.id_familia = None
    db.commit()
    return {"mensaje": "Miembro removido"}

# 5. ELIMINAR GRUPO FAMILIAR COMPLETO (Solo el Jefe)
@app.delete("/familias/disolver/{id_familia}")
def disolver_familia(id_familia: int, id_jefe: int, db: Session = Depends(get_db)):
    familia = db.query(models.Familia).filter(
        models.Familia.id_familia == id_familia,
        models.Familia.id_jefe == id_jefe
    ).first()

    if not familia:
        raise HTTPException(status_code=403, detail="No tienes permiso para disolver este grupo o no existe")

    try:
        db.query(models.Usuario).filter(models.Usuario.id_familia == id_familia).update({"id_familia": None})
        db.delete(familia)
        db.commit()
        return {"mensaje": "Grupo familiar disuelto. Todos los miembros son ahora independientes."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al disolver: {str(e)}")

# --- RUTAS DE ACTIVIDADES ---

@app.post("/actividades/", response_model=schemas.ActividadResponse)
def crear_actividad(actividad: schemas.ActividadCreate, db: Session = Depends(get_db)):
    # Usamos el CRUD actualizado para que no haya errores de lógica
    return crud.crear_actividad(db=db, actividad=actividad)

@app.get("/familias/{id_familia}/actividades")
def listar_actividades(id_familia: int, db: Session = Depends(get_db)):
    # Filtra actividades por el ID de la familia
    return db.query(models.Actividad).filter(models.Actividad.id_familia == id_familia).all()

@app.delete("/actividades/{id_actividad}")
def borrar_actividad(id_actividad: int, db: Session = Depends(get_db)):
    act = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
    if not act:
        raise HTTPException(status_code=404, detail="No existe")
    db.delete(act)
    db.commit()
    return {"mensaje": "Eliminada"}