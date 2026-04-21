from fastapi import FastAPI, Depends, HTTPException
from flet import app
from sqlalchemy.orm import Session
from backend import crud, models, schemas
from backend.database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

# Creamos las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bondify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier app se conecte
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (POST, GET, etc)
    allow_headers=["*"],
)

# Función para conectar con la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# RUTA 1: Para el botón de "Registrarse"
@app.post("/usuarios/", response_model=schemas.Usuario)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificamos si el correo ya existe
    db_usuario = crud.get_usuario_by_email(db, email=usuario.correo)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return crud.crear_usuario(db=db, usuario=usuario)

# RUTA 2: Para los botones de tu dibujo (Login por correo o número)
@app.post("/login/")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    user = None
    if usuario.correo:
        user = crud.get_usuario_by_email(db, usuario.correo)
    elif usuario.telefono:
        user = crud.get_usuario_by_telefono(db, usuario.telefono)
    
    if not user or user.contrasena != usuario.contrasena:
        raise HTTPException(status_code=400, detail="Datos incorrectos")
    
    return {"mensaje": "Inicio de sesión exitoso", "usuario": user.nombre, "rol": user.tipo_usuario}

#ese codigo de python -m backend.main es para ejecutar este archivo main.py y así crear las tablas en la base de datos MySQL. Asegúrate de tener MySQL corriendo y la base de datos 'bondify_db' creada antes de ejecutar este comando.