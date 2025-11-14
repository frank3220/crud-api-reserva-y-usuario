from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict # Importamos ConfigDict

# Esquema Base para datos comunes
class ReservationBase(BaseModel):
    # Campos que el usuario proporciona al crear o actualizar
    fecha: date = Field(..., description="Fecha de la reserva (YYYY-MM-DD)")
    hora: time = Field(..., description="Hora de inicio de la reserva (HH:MM:SS)")
    tiempo: int = Field(..., description="Duración de la reserva en horas")
    numhabitacion: str = Field(..., description="Número de la habitación reservada")
    tipopago: str = Field(..., description="Tipo de pago utilizado")
    valor: float = Field(..., gt=0, description="Valor total de la reserva")
    userid: int = Field(..., description="ID del usuario que realiza la reserva")

# 1. Esquema para Crear una nueva Reserva (Input/POST)
class ReservationCreate(ReservationBase):
    # keyreserva se podría generar automáticamente, pero lo incluimos si es requerido al crear
    keyreserva: str = Field(..., description="Clave única o código de la reserva")
    # *** CORRECCIÓN: AGREGAMOS EL ESTADO YA QUE ES REQUERIDO POR EL REPOSITORIO ***
    estado: str = Field(..., description="Estado inicial de la reserva (p. ej., 'Pendiente')")

# 2. Esquema para Actualizar una Reserva (Input/PATCH)
class ReservationUpdate(ReservationBase):
    # Todos los campos son opcionales para una actualización parcial (PATCH)
    keyreserva: Optional[str] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    tiempo: Optional[int] = None
    numhabitacion: Optional[str] = None
    tipopago: Optional[str] = None
    valor: Optional[float] = None
    userid: Optional[int] = None
    estado: Optional[str] = None # Podemos permitir actualizar el estado (p. ej., 'confirmada', 'cancelada')

# 3. Esquema para la Respuesta (Output)
class Reservation(ReservationBase):
    idreserva: int = Field(..., description="ID autogenerado de la reserva")
    keyreserva: str # Repetimos keyreserva ya que es parte del modelo final
    estado: str = Field(..., description="Estado actual de la reserva (p. ej., 'Pendiente')") # Se repite aquí para la respuesta

    # Sintaxis V2: Reemplazamos 'class Config' por 'model_config'
    model_config = ConfigDict(from_attributes=True)