from sqlalchemy import Column, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from dependencies.database import Base


class CompraDetalle(Base):
    __tablename__ = "compra_detalle"

    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_compra = Column(Integer, ForeignKey("compras_proveedor.id_compra"), nullable=False)
    id_producto = Column(Integer, ForeignKey("tsproductos.id_producto"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(DECIMAL(12, 2), nullable=False)

    compra = relationship("ComprasProveedor", back_populates="detalles")
    # --- AÑADE ESTA LÍNEA PARA CARGAR EL NOMBRE ---
    producto_rel = relationship("Producto", lazy="joined")
