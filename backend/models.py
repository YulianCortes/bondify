from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from backend.database import Base 

class Familia(Base):
    __tablename__ = "familias"
    
    id_familia = Column(Integer, primary_key=True, index=True)
    nombre_familia = Column(String(100), nullable=False)
    id_jefe = Column(Integer, ForeignKey("usuarios.id_usuario"))

    # Relación: Una familia tiene muchos miembros
    miembros = relationship("Usuario", back_populates="familia", foreign_keys="[Usuario.id_familia]")
    
    # NUEVO: Una familia tiene muchas actividades asignadas o sugeridas
    actividades = relationship("Actividad", back_populates="familia")

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    telefono = Column(String(20), unique=True)
    contrasena = Column(String(100))
    tipo_usuario = Column(String(50), default="Familiar") 
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
    actividades_asignadas = relationship("Actividad", back_populates="usuario_asignado")

class Actividad(Base):
    __tablename__ = "actividades"
    
    id_actividad = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    descripcion = Column(String(255))
    es_sugerencia = Column(Boolean, default=True)
    aprobada = Column(Boolean, default=False)
    
    # Foreign Keys
    id_familia = Column(Integer, ForeignKey("familias.id_familia"), nullable=True)
    id_usuario_asignado = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    # Relaciones
    # NUEVO: La actividad pertenece a una familia
    familia = relationship("Familia", back_populates="actividades")
    # La actividad le pertenece a un usuario específico (quien debe hacerla)
    usuario_asignado = relationship("Usuario", back_populates="actividades_asignadas")