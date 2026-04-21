from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database import Base # Importamos la Base que acabas de crear

class Usuario(Base):
    __tablename__ = "usuarios"

    # Definición de campos (Atributos de tu clase de Java)
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True, index=True)
    telefono = Column(String(20), unique=True)
    contrasena = Column(String(255))
    
    # Rol: Aquí es donde controlaremos si es 'Jefe' o 'Familiar'
    tipo_usuario = Column(String(50)) 
    
    # Sistema de puntos para las tareas
    puntos = Column(Integer, default=0)

class Actividad(Base):
    __tablename__ = "actividades"

    id_actividad = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    descripcion = Column(String(255))
    estado = Column(String(50), default="Pendiente") # Por defecto al crearla
    
    # Relación: Conecta la actividad con el ID del usuario responsable
    id_usuario_asignado = Column(Integer, ForeignKey("usuarios.id_usuario"))