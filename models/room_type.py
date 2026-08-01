from sqlalchemy import Column, Integer, String, Float
from dependencies.database import Base

class RoomType(Base):
    __tablename__ = "ts_room_types"

    id = Column(Integer, primary_key=True, index=True)
    # CORREGIDO: Se agregó la longitud (ej. 50) a String
    nombre = Column(String(50), unique=True, index=True, nullable=False)
    tarifa_por_hora = Column(Float, nullable=False)
    # CORREGIDO: Se agregó la longitud (ej. 255) a String
    descripcion = Column(String(255), nullable=True)