from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

URL_DATABASE = "mysql+pymysql://root:123456789@localhost:3306/bondify_db"

# El motor que conectará Python con MySQL
engine = create_engine(URL_DATABASE)

# La fábrica de sesiones para hacer consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La clase base de la que heredarán los modelos (Usuario, Actividad, etc.)
Base = declarative_base()

# Función para obtener la conexión y cerrarla automáticamente al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()