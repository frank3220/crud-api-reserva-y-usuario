from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship 
# Asegúrate de que la importación de 'Base' sea correcta, aquí usamos 'dependencies.database' por convención
from dependencies.database import Base 

# CRÍTICO: Importamos la Reserva para que la relación funcione. 
# Si esta línea da error (importación circular), puedes usar el string "ReservationModel".
# Dejaré el string para mayor seguridad:
# from .reservation import ReservationModel 

class Usuario(Base):

    __tablename__ = 'usuarios'

    # CLAVE PRIMARIA: Debe ser 'idusuario' para que la reserva apunte a ella
    idusuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    nombre = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    rol = Column(String(50))
    
    # RELACIÓN: Permite acceder a las reservas de este usuario.
    # El 'viewonly=True' SOLUCIONA el error 500 al serializar el objeto Usuario.
    usuario_reservas = relationship("ReservationModel", back_populates="reservacion_usuario", viewonly=True)