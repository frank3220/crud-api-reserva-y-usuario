from sqlalchemy import (
    Column, Integer, Date, DECIMAL, String, Text,
    TIMESTAMP, func, ForeignKey
)
from dependencies.database import Base
from models.arqueo import ArqueoTurno # 👈 AGREGA ESTA LÍNEA


class AcpmLog(Base):
    __tablename__ = "acpm_log"

    id_acpm = Column(Integer, primary_key=True, index=True)

    fecha = Column(Date, nullable=False)
    litros = Column(DECIMAL(10, 2), nullable=False)
    valor_total = Column(DECIMAL(12, 2), nullable=False)
    proveedor = Column(String(150), nullable=True)
    nota = Column(Text, nullable=True)

    # Control crédito
    tipo_pago = Column(String(20), default="contado")
    saldo_pendiente = Column(DECIMAL(12, 2), default=0)
    pagado = Column(Integer, default=0)
    fecha_pago = Column(Date, nullable=True)

    # ✅ Ajustamos el ForeignKey al nombre real de la tabla de arqueos
    #id_arqueo = Column(Integer, ForeignKey("tsarqueo.id_arqueo"), nullable=True)
    id_arqueo = Column(Integer, ForeignKey(ArqueoTurno.id_arqueo), nullable=True)

    creado = Column(TIMESTAMP, server_default=func.now())