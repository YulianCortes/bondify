from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from backend.database import Base 

# --- TABLA PUENTE PARA MULTI-ASIGNACIÓN ---
class AsignacionActividad(Base):
    __tablename__ = "asignaciones_actividades"
    
    id_asignacion = Column(Integer, primary_key=True, index=True)
    id_actividad = Column(Integer, ForeignKey("actividades.id_actividad", ondelete="CASCADE"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))

class Familia(Base):
    __tablename__ = "familias"
    
    id_familia = Column(Integer, primary_key=True, index=True)
    nombre_familia = Column(String(100), nullable=False)
    id_jefe = Column(Integer, ForeignKey("usuarios.id_usuario"))
    
    # NUEVO: Puntos totales de la familia para el sistema de racha (Niveles mascota)
    puntos_familia = Column(Integer, default=0)

    # Relación: Una familia tiene muchos miembros
    miembros = relationship("Usuario", back_populates="familia", foreign_keys="[Usuario.id_familia]")
    
    # Una familia tiene muchas actividades
    actividades = relationship("Actividad", back_populates="familia")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    telefono = Column(String(20), unique=True)
    contrasena = Column(String(100))
    tipo_usuario = Column(String(50), default="Familiar") 
    
    # Puntos individuales del usuario (+5 / -5)
    puntos = Column(Integer, default=0)
    
    disponibilidad_semanal = Column(String(500), default="Sin horario definido")

    # Campos de perfil
    primer_nombre = Column(String(100), nullable=True)
    primer_apellido = Column(String(100), nullable=True)
    edad = Column(Integer, nullable=True)
    genero = Column(String(50), nullable=True)
    biografia = Column(Text, nullable=True)
    url_avatar = Column(String(255), default="assets/default_avatar.png")
    
    # Conexión con Familia
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=True)
    
    # Relaciones
    familia = relationship("Familia", back_populates="miembros", foreign_keys=[id_familia])
    
    # Relación Muchos a Muchos con Actividades
    actividades_asignadas = relationship("Actividad", secondary="asignaciones_actividades", back_populates="usuarios_asignados")

class Actividad(Base):
    __tablename__ = "actividades"
    
    id_actividad = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    descripcion = Column(String(255))
    es_sugerencia = Column(Boolean, default=True)
    aprobada = Column(Boolean, default=False)
    
    # NUEVO: Para saber si el jefe ya calificó y terminó esta tarea
    terminada = Column(Boolean, default=False)
    
    # NUEVO: FECHA PARA EL CALENDARIO (Sincronización real)
    # Aquí es donde guardaremos que la actividad es para el 27/04/2026
    fecha = Column(Date, nullable=True)
    
    # Foreign Keys
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=True)
    
    # Relaciones
    familia = relationship("Familia", back_populates="actividades")
    
    # Relación Muchos a Muchos con Usuarios (EQUIPO)
    usuarios_asignados = relationship("Usuario", secondary="asignaciones_actividades", back_populates="actividades_asignadas")