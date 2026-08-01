from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dependencies.database import Base
import enum

class EstadoOcupacion(str, enum.Enum):
    OCUPADA = "OCUPADA"
    LIBERADA = "LIBERADA"
    ANULADA = "ANULADA"  # ✅ Nuevo estado para las cancelaciones

class Ocupacion(Base):
    __tablename__ = "ocupaciones"

    id_ocupacion = Column(Integer, primary_key=True, index=True, autoincrement=True)

    id_habitacion = Column(
        Integer, 
        ForeignKey("tshabitacion.id_habitacion"), 
        nullable=False
    )

    # 🔐 Auditoría: Quién hizo qué
    usuario_id = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=True) # Entrada / Cierre
    id_usuario_salida = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=True) # ✅ Nuevo
    id_usuario_anulacion = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=True) # ✅ Nuevo

    hora_entrada = Column(DateTime, server_default=func.now())
    hora_salida = Column(DateTime, nullable=True)
    fecha_anulacion = Column(DateTime, nullable=True) # ✅ Nuevo

    estado = Column(Enum(EstadoOcupacion), default=EstadoOcupacion.OCUPADA)
    total_pagar = Column(Float, nullable=True)
    observaciones = Column(String(200), nullable=True)

    activa = Column(Boolean, default=True)
    
    # ✅ Método de pago
    metodo_pago = Column(String(20), default="efectivo")
    
    # 🕒 Vínculo con el Turno (Arqueo)
    id_arqueo = Column(Integer, ForeignKey("tsarqueo_turno.id_arqueo"), nullable=True)

    # Relaciones
    habitacion = relationship("tshabitacion")
    
    # 🔥 Relación con Usuario (el principal)
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="ocupaciones")
    
    # Opcional: Relaciones para los otros usuarios si necesitas reportes detallados
    usuario_salida = relationship("Usuario", foreign_keys=[id_usuario_salida])
    usuario_anulacion = relationship("Usuario", foreign_keys=[id_usuario_anulacion])

    # 🔥 Relación con el Turno/Arqueo
    arqueo_turno = relationship("ArqueoTurno", back_populates="ocupaciones")