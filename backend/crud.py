from sqlalchemy.orm import Session
from backend import models, schemas

# Función para BUSCAR un usuario por correo (útil para el login)
def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.correo == email).first()

# Función para BUSCAR un usuario por teléfono (para tu botón de "con número")
def get_usuario_by_telefono(db: Session, telefono: str):
    return db.query(models.Usuario).filter(models.Usuario.telefono == telefono).first()

# Función para CREAR un usuario (El Registro)
def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    # En un proyecto real, aquí cifraríamos la contraseña. 
    # Por ahora, la guardamos directo para que sea más fácil para ti.
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        telefono=usuario.telefono,
        contrasena=usuario.contrasena,
        tipo_usuario=usuario.tipo_usuario,
        puntos=0 # Todos empiezan con 0 puntos
    )
    db.add(db_usuario)
    db.commit() # Guarda los cambios en MySQL
    db.refresh(db_usuario) # Nos devuelve el usuario con su ID ya generado
    return db_usuario