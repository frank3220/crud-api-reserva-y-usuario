from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from dependencies.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False, unique=True)
    telefono = Column(String(50), nullable=True)
    nit = Column(String(50), nullable=True)
    activo = Column(Boolean, default=True)

    # ✅ RELACIÓN INVERSA
    compras = relationship(
        "ComprasProveedor",
        back_populates="proveedor"
    )
    gastos_lista = relationship("Gasto", back_populates="proveedor_rel")
