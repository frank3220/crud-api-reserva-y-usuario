from sqlalchemy import Column, Integer, String, Date, Text, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from dependencies.database import Base 

class Gasto(Base):
    __tablename__ = "gastos"

    id_gasto = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False, default=func.current_date())
    concepto = Column(String(150), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    cantidad = Column(Integer, default=1) # <--- AGREGA ESTA LÍNEA
    # Conexión con proveedores
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=True)
    proveedor = Column(String(150), nullable=True) 
    
    nota = Column(Text, nullable=True)
    tipo_pago = Column(String(20), default="contado")
    
    # ✅ COLUMNA CONFIRMADA: Para el amarre automático del arqueo
    id_arqueo = Column(Integer, nullable=True)
    
    creado = Column(DateTime, default=datetime.now) # Cambiado a local para coincidir con tsventas

    # Relaciones
    # Asegúrate de que en el modelo de Proveedor el back_populates coincida
    proveedor_rel = relationship("Proveedor", back_populates="gastos_lista")