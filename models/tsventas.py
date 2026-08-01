from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from dependencies.database import Base 

class tsventas(Base):
    __tablename__ = 'tsventas'
    
    id_venta = Column(Integer, primary_key=True, index=True)
    tsfecha = Column(DateTime, default=datetime.now)
    id_habitacion = Column(Integer, ForeignKey('tshabitacion.id_habitacion'), nullable=False)
    tsvalor = Column(Float, nullable=False, default=0.0) 
    tsconsumo = Column(Float, nullable=False, default=0.0) 
    tsentrada = Column(DateTime, default=datetime.now) 
    tssalida = Column(DateTime, nullable=True) 
    tsestado = Column(String(20), nullable=False, default='ACTIVA') 
    tsduracion_inicial = Column(Integer, default=120) 
    tsobservaciones = Column(Text, nullable=True)

    # ✅ COLUMNA CRÍTICA: Para el arqueo automático
    id_arqueo = Column(Integer, nullable=True) 

    # ✅ COLUMNA: Para conectar con la tabla usuarios
    id_usuario_registro = Column(Integer, ForeignKey('usuarios.idusuario'), nullable=True)
    
    # Relaciones
    habitacion = relationship("tshabitacion")
    #usuario_relacion = relationship("Usuarios")
    usuario_relacion = relationship("Usuario")