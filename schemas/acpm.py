from pydantic import BaseModel
from datetime import date, datetime


# 🟩 Datos para CREAR un registro ACPM (contado o crédito)
class ACPMCreate(BaseModel):
    fecha: date
    litros: float
    valor_total: float
    proveedor: str | None = None
    nota: str | None = None
    tipo_pago: str = "contado"   # contado o credito


# 🟩 Datos para ABONAR a un crédito
class ACPMAbono(BaseModel):
    monto: float   # valor del abono


# 🟩 Salida de un registro ACPM (lo que devuelve la API)
class ACPMOut(BaseModel):
    id_acpm: int
    fecha: date
    litros: float
    valor_total: float
    proveedor: str | None
    nota: str | None
    tipo_pago: str
    saldo_pendiente: float
    pagado: bool
    fecha_pago: date | None
    creado: datetime

    model_config = {
        "from_attributes": True
    }


# 🟩 Salida para créditos pendientes
class ACPMCreditoOut(BaseModel):
    id_acpm: int
    fecha: date
    proveedor: str | None
    valor_total: float
    saldo_pendiente: float
    nota: str | None
    creado: datetime

    model_config = {
        "from_attributes": True
    }
