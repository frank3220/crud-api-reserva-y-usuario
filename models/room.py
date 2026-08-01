from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from dependencies.database import Base
from datetime import datetime


class tshabitacion(Base):
    __tablename__ = "tshabitacion"

    id_habitacion = Column(Integer, primary_key=True, index=True)
    numhabitacion = Column(String(10), nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    capacidad = Column(Integer, nullable=False)

    precio_2h = Column(Float, nullable=False)
    precio_hora_adicional = Column(Float, nullable=False)

    estado = Column(String(50), default="DISPONIBLE")
    descripcion = Column(String(255), nullable=True)

    activa = Column(Boolean, default=True)

    # 🔥 NUEVA COLUMNA PARA AUTO-LIMPIEZA
    hora_limpiar = Column(DateTime, nullable=True)
   
