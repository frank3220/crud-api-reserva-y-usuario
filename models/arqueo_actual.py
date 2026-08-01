from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from dependencies.database import Base


class ArqueoActual(Base):
    __tablename__ = "arqueo_actual"

    id = Column(Integer, primary_key=True, index=True)
    consecutivo = Column(Integer, default=1)

    fecha_inicio = Column(DateTime, server_default=func.now())

    total_ventas = Column(Float, default=0)
    total_acpm = Column(Float, default=0)
    total_gastos = Column(Float, default=0)
    neto = Column(Float, default=0)

    # ✅ NUEVAS COLUMNAS PARA EL DESGLOSE DE PAGOS
    ventas_efectivo = Column(Float, default=0)
    ventas_nequi = Column(Float, default=0)
    ventas_datafono = Column(Float, default=0)

    actualizado = Column(DateTime, server_default=func.now(), onupdate=func.now())