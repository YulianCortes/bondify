from pydantic import BaseModel, EmailStr
from typing import Optional

# Esquema base para el Usuario (lo que comparten registro e inicio de sesión)
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    tipo_usuario: str # Aquí recibiremos 'Jefe' o 'Familiar'

# Esquema específico para cuando alguien se REGISTRA
# (Pedimos la contraseña)
class UsuarioCreate(UsuarioBase):
    contrasena: str

# Esquema para cuando mostramos un usuario (No mostramos la contraseña por seguridad)
class Usuario(UsuarioBase):
    id_usuario: int
    puntos: int

    class Config:
        from_attributes = True

# Esquema para el Inicio de Sesión (Login)
class UsuarioLogin(BaseModel):
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    contrasena: str