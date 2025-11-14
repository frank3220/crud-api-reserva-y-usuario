from sqlalchemy import Column, Integer, String, Date, Time, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from dependencies.database import Base # Asegúrate de que esta importación sea correcta

# ❌ IMPORTACIÓN ELIMINADA: Ya no importamos 'Usuario' para evitar la dependencia circular.

# Esta es la clase que el repositorio está intentando importar.
class ReservationModel(Base):
    
    # Nombre de la tabla en la base de datos (CRÍTICO)
    __tablename__ = "reservations" 

    idreserva = Column(Integer, primary_key=True, index=True)
    keyreserva = Column(String(50), unique=True, index=True)
    estado = Column(String(50))
    fecha = Column(Date)
    hora = Column(Time)
    tiempo = Column(Integer)
    numhabitacion = Column(String(50))
    tipopago = Column(String(50))
    valor = Column(Numeric(10, 2))
    
    # CLAVE FORÁNEA
    userid = Column(Integer, ForeignKey('usuarios.idusuario'), nullable=False) 

    # ✅ CORRECCIÓN FINAL: La relación usa el string "Usuario" y tiene viewonly=True.
    reservacion_usuario = relationship("Usuario", back_populates="usuario_reservas", viewonly=True)