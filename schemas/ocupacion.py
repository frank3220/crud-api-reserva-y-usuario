from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class EstadoOcupacion(str, Enum):
    OCUPADA = "OCUPADA"
    LIBERADA = "LIBERADA"
    ANULADA = "ANULADA" # ✅ Agregado para soportar anulaciones

class OcupacionBase(BaseModel):
    id_habitacion: int
    observaciones: Optional[str] = None # Corregido a plural para que coincida con el modelo (observaciones)
    usuario_id: Optional[int] = None 

    class Config:
        from_attributes = True 

# ... (lo anterior queda igual)

class OcupacionCreate(OcupacionBase):
    # Añadimos estos dos para capturar el monto manual y el tipo
    tarifa: float 
    es_amanecida: bool = False

class OcupacionUpdate(BaseModel):
    total_pagar: float
    usuario_id: Optional[int] = None   
    metodo_pago: str = "efectivo" 
    es_amanecida: Optional[bool] = False

    class Config:
        from_attributes = True

class OcupacionResponse(BaseModel):
    id_ocupacion: int
    id_habitacion: int
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None
    fecha_anulacion: Optional[datetime] = None 
    estado: str 
    total_pagar: Optional[float] = None
    observaciones: Optional[str] = None
    activa: bool
    metodo_pago: Optional[str] = "efectivo" 
    
    # --- AÑADIMOS ESTO PARA LA RESPUESTA ---
    es_amanecida: bool = False 
    
    # IDs de Auditoría
    usuario_id: Optional[int] = None 
    id_usuario_salida: Optional[int] = None 
    id_usuario_anulacion: Optional[int] = None 

    class Config:
        from_attributes = True