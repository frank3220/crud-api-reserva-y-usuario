from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from dependencies.database import Base

class KardexInventario(Base):
    __tablename__ = "kardex_inventario"

    id_kardex = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, nullable=False)  # ❌ SIN ForeignKey
    fecha = Column(DateTime, default=func.now())
    tipo_movimiento = Column(String(20), nullable=False)  # ENTRADA / SALIDA
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_nuevo = Column(Integer, nullable=False)
    referencia = Column(String(100), nullable=True)
