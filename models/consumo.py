from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from dependencies.database import Base


class Consumo(Base):
    __tablename__ = "tsconsumos"

    id_consumo = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    concepto = Column(String(150), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    valor = Column(DECIMAL(12, 2), nullable=False)
    nota = Column(String(255), nullable=True)

    # ✅ EXISTE EN BD → SIN FK
    id_producto = Column(Integer, nullable=True)

    id_arqueo = Column(Integer, ForeignKey("tsarqueo_turno.id_arqueo"), nullable=True)

    # vínculo con ocupación
    id_ocupacion = Column(Integer, nullable=True)

    creado = Column(TIMESTAMP, server_default=func.now())

    # relación arqueo
    arqueo = relationship("ArqueoTurno", back_populates="consumos")
