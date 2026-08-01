from sqlalchemy import Column, Integer, ForeignKey, Date, DECIMAL, VARCHAR, TEXT, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from dependencies.database import Base


class ComprasProveedor(Base):
    __tablename__ = "compras_proveedor"

    id_compra = Column(Integer, primary_key=True, autoincrement=True)

    # ✅ CORRECTO: la tabla es "proveedores"
    id_proveedor = Column(
        Integer,
        ForeignKey("proveedores.id_proveedor"),
        nullable=False
    )

    fecha = Column(Date, nullable=False)
    total = Column(DECIMAL(12, 2), nullable=False)

    tipo_pago = Column(VARCHAR(20), default="contado")
    nota = Column(TEXT, nullable=True)
    creado = Column(TIMESTAMP, server_default=func.current_timestamp())

    # ✅ EXISTE EN TU BD (MariaDB) – SIN ForeignKey para evitar problemas
    id_arqueo = Column(Integer, nullable=True)

    # Relaciones
    detalles = relationship(
        "CompraDetalle",
        back_populates="compra",
        cascade="all, delete-orphan"
    )

    proveedor = relationship(
        "Proveedor",
        back_populates="compras"
    )
