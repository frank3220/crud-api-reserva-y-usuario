from sqlalchemy import Column, Integer, DateTime, DECIMAL, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from dependencies.database import Base

class ArqueoTurno(Base):
    __tablename__ = "tsarqueo_turno"

    id_arqueo = Column(Integer, primary_key=True, index=True)
    
    # 👤 Quién abrió este turno
    id_usuario = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=False)
    
    fecha_inicio = Column(DateTime, nullable=False, server_default=func.now())
    fecha_fin = Column(DateTime, nullable=True) 

    consecutivo = Column(Integer, nullable=False)

    total_ventas = Column(DECIMAL(12, 2), default=0)
    total_acpm = Column(DECIMAL(12, 2), default=0)
    total_gastos = Column(DECIMAL(12, 2), default=0)
    total_consumos = Column(DECIMAL(12, 2), default=0) 
    neto = Column(DECIMAL(12, 2), default=0)


    ventas_nequi = Column(DECIMAL(12, 2), default=0)
    ventas_datafono = Column(DECIMAL(12, 2), default=0)
    # 🔥 AGREGA ESTAS 3 LÍNEAS AQUÍ:
    total_acpm_credito = Column(DECIMAL(12, 2), default=0)
    total_gastos_credito = Column(DECIMAL(12, 2), default=0)
    total_compras_credito = Column(DECIMAL(12, 2), default=0)

    creado_en = Column(TIMESTAMP, server_default=func.now())
    nota = Column(DECIMAL(12, 2), nullable=True)

    
    usuario = relationship("Usuario") 
    consumos = relationship("Consumo", back_populates="arqueo")
    ocupaciones = relationship("Ocupacion", back_populates="arqueo_turno")