from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class CompraDetalleCreate(BaseModel):
    id_producto: int
    cantidad: int
    costo_unitario: float


class CompraProveedorCreate(BaseModel):
    id_proveedor: int
    fecha: date
    tipo_pago: str  # contado | credito (llega como CONTADO/CREDITO y lo normalizamos en el router)
    nota: Optional[str] = None
    detalles: List[CompraDetalleCreate]
