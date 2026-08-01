from pydantic import BaseModel
from typing import Optional
from datetime import date

class ConsumoCreate(BaseModel):
    fecha: date
    concepto: str
    cantidad: int
    valor: float
    nota: Optional[str] = None

    # 🔥 CLAVE: ahora es opcional
    id_ocupacion: Optional[int] = None

    # producto del catálogo
    id_producto: Optional[int] = None
