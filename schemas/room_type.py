from pydantic import BaseModel
from typing import Optional

class RoomTypeBase(BaseModel):
    nombre: str
    tarifa_por_hora: float
    descripcion: Optional[str] = None

class RoomTypeCreate(RoomTypeBase):
    pass

class RoomTypeOut(RoomTypeBase):
    id: int

    class Config:
        from_attributes = True