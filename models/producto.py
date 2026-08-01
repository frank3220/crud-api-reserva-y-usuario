from sqlalchemy import Column, Integer, String, Float, Boolean
from dependencies.database import Base

class Producto(Base):
    __tablename__ = "tsproductos"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)

   # stock = Column(Integer, default=0)  # 🔥 ESTE ES EL INVENTARIO REAL
    activo = Column(Boolean, default=True)
