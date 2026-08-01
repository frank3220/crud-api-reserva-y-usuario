# dependencies/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from sqlalchemy.orm import Session


# ======================================================
# 1. CONFIGURACIÃ“N DEL MOTOR Y BASE
# ======================================================
from utils.settings import DATABASE_URL
SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,          # Evita conexiones muertas
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos â€” debe declararse *antes* de importar modelos
Base = declarative_base()


# ======================================================
# 2. FUNCIÃ“N get_db
# ======================================================
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================================================
# 3. IMPORTACIÃ“N DE MODELOS (DESPUÃ‰S DE CREAR Base)
# ======================================================
# âš ï¸ IMPORTANTE
# Estos imports SIEMPRE DEBEN ESTAR AL FINAL
# para evitar CIRCULAR IMPORTS.
# ======================================================

from models.ocupacion import Ocupacion
from models.room import tshabitacion
from models.acpm import AcpmLog
from models.arqueo import ArqueoTurno
from models.arqueo_actual import ArqueoActual  # â† ya puedes importarlo sin error


# ======================================================
# 4. CREACIÃ“N AUTOMÃTICA DE TABLAS
# ======================================================
Base.metadata.create_all(bind=engine)

