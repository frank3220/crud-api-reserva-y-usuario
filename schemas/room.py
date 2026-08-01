from pydantic import BaseModel, Field
from typing import Optional

# ------------------------------------------------
# BASE
# ------------------------------------------------
class RoomBase(BaseModel):
    numhabitacion: str
    nombre: str
    tipo: str
    capacidad: int
    precio_2h: float
    precio_hora_adicional: float
    
    # 🚀 CORRECCIÓN AQUÍ: Ahora es opcional y tiene un valor por defecto seguro
    estado: Optional[str] = "DISPONIBLE" 
    
    descripcion: Optional[str] = None
    activa: bool = True

# ------------------------------------------------
# CREATE
# ------------------------------------------------
class RoomCreate(RoomBase):
    pass

# ------------------------------------------------
# UPDATE
# ------------------------------------------------
class RoomUpdate(RoomBase):
    numhabitacion: Optional[str] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    capacidad: Optional[int] = None
    precio_2h: Optional[float] = None
    precio_hora_adicional: Optional[float] = None
    estado: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None

# ------------------------------------------------
# OUT
# ------------------------------------------------
class RoomOut(RoomBase):
    id_habitacion: int

    class Config:
        from_attributes = True

# ------------------------------------------------
# FULL OUT (USADO POR /rooms/)
# ------------------------------------------------
class RoomFullOut(RoomOut):
    status: str
    entrada: Optional[str] = None
    id_ocupacion: Optional[int] = None

    # 🔥 CLAVE PARA EL FRONTEND
    total_consumos: float = 0
    activa: Optional[bool | int] = True
    