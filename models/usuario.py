from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from dependencies.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    idusuario = Column(Integer, primary_key=True, index=True, autoincrement=True)

    nombre = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    rol = Column(String(50))
    activo = Column(Boolean, default=True)

    # 🔥 RELACIÓN CON OCUPACIONES (Ya la teníamos)
    ocupaciones = relationship("Ocupacion", foreign_keys="[Ocupacion.usuario_id]", back_populates="usuario")

    # 🔥 RELACIÓN CON RESERVAS (Esta es la que faltaba y causaba el error 500)
    # Debe llamarse 'usuario_reservas' y apuntar a 'reservacion_usuario' en ReservationModel
    usuario_reservas = relationship("ReservationModel", back_populates="reservacion_usuario")