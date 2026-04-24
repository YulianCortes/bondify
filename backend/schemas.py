from pydantic import BaseModel, EmailStr
from typing import Optional, List

# --- ESQUEMAS DE USUARIO ---

class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    tipo_usuario: Optional[str] = "Familiar" 
    disponibilidad_semanal: Optional[str] = "Sin horario definido"

class UsuarioCreate(UsuarioBase):
    contrasena: str

class Usuario(UsuarioBase):
    id_usuario: int
    puntos: int

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    contrasena: str

class UsuarioUpdate(BaseModel):
    primer_nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    edad: Optional[int] = None
    genero: Optional[str] = None
    biografia: Optional[str] = None
    disponibilidad_semanal: Optional[str] = None

# --- ESQUEMAS DE FAMILIA ---

class FamiliaBase(BaseModel):
    nombre_familia: str

class FamiliaCreate(FamiliaBase):
    id_jefe: int

class FamiliaResponse(FamiliaBase):
    id_familia: int
    id_jefe: int
    class Config:
        from_attributes = True

# Este esquema es para los objetos individuales dentro de la lista de integrantes
class MiembroFamilia(BaseModel):
    id_usuario: int
    nombre: str
    primer_nombre: Optional[str] = None
    rol: str

# --- NUEVO: Esquema para la respuesta completa de la familia ---
class FamiliaDetalle(BaseModel):
    nombre_familia: str
    id_jefe: int
    integrantes: List[MiembroFamilia]
    mensaje: Optional[str] = None

class ActividadBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None

class ActividadCreate(ActividadBase):
    id_familia: int
    es_sugerencia: bool = True

class ActividadResponse(ActividadBase):
    id_actividad: int
    es_sugerencia: bool
    aprobada: bool
    id_usuario_asignado: Optional[int]
    class Config:
        from_attributes = True