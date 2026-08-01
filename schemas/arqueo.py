# schemas/arqueo.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

class VentaItemOut(BaseModel):
    id_ocupacion: int
    id_habitacion: int
    numhabitacion: str
    total: float
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None

class AcpmItemOut(BaseModel):
    id_acpm: int
    fecha: datetime
    litros: float
    valor_total: float
    proveedor: Optional[str] = None

class GastoItemOut(BaseModel):
    id_gasto: int
    descripcion: str
    valor: float
    categoria: Optional[str] = None

class ArqueoResumen(BaseModel):
    id_arqueo: Optional[int] = None
    consecutivo: Optional[int] = None
    fecha: date

    total_ventas: float
    total_acpm: float
    total_gastos: float
    neto: float

    ventas: List[VentaItemOut]
    acpm: List[AcpmItemOut]
    gastos: List[GastoItemOut] = []

    class Config:
        from_attributes = True
