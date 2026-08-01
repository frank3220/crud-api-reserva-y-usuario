# models/configuracion.py
from sqlalchemy import Column, Integer, String, DateTime, func
from dependencies.database import Base

class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(String(100), nullable=False)
    descripcion = Column(String(250), nullable=True)
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
