from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from sqlalchemy.orm import Session # Importado para tipado


# ----------------------------------------------------
# 1. Configuración de la URL de la Base de Datos
# La URL de tu base de datos MariaDB (mluna) es correcta.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root123@127.0.0.1:3306/mluna"
# ----------------------------------------------------

# Crea el motor de SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # ❌ SE ELIMINÓ: El argumento connect_args es inválido para MariaDB/MySQL 
    #                y causaba el error 'check_same_thread'.
)

# Crea la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# ----------------------------------------------------
# 2. La función de dependencia 'get_db' (Generador)
# ----------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  # Proporciona la sesión al endpoint/servicio
    finally:
        db.close() # Asegura que la sesión se cierre después de la petición