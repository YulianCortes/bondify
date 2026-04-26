from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

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
    puntos: int # Puntos individuales para el ranking

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

class UsuarioResumen(BaseModel):
    id_usuario: int
    nombre: str
    class Config:
        from_attributes = True

# --- ESQUEMAS DE FAMILIA ---

class FamiliaBase(BaseModel):
    nombre_familia: str

class FamiliaCreate(FamiliaBase):
    id_jefe: int

class FamiliaResponse(FamiliaBase):
    id_familia: int
    id_jefe: int
    puntos_familia: int = 0 # IMPORTANTE: Para que el Home sepa el nivel inicial
    class Config:
        from_attributes = True

class MiembroFamilia(BaseModel):
    id_usuario: int
    nombre: str
    primer_nombre: Optional[str] = None
    rol: str
    puntos: int = 0 # Para mostrar cuánto ha aportado cada uno
    disponibilidad: Optional[str] = None

class FamiliaDetalle(BaseModel):
    nombre_familia: str
    id_jefe: int
    puntos_familia: int = 0 # El motor de la racha
    integrantes: List[MiembroFamilia]
    mensaje: Optional[str] = None

# --- ESQUEMAS DE ACTIVIDADES ---

class ActividadBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    # NUEVO: Fecha para que el calendario sepa dónde poner el punto naranja
    fecha: Optional[date] = None 

class ActividadCreate(ActividadBase):
    id_familia: int
    es_sugerencia: bool = True

class ActividadResponse(ActividadBase):
    id_actividad: int
    es_sugerencia: bool
    aprobada: bool = False # AGREGADO: Para que el frontend sepa si ya fue aceptada
    terminada: bool = False # Para filtrar las que ya se calificaron
    usuarios_asignados: List[UsuarioResumen] = [] 
    
    class Config:
        from_attributes = True