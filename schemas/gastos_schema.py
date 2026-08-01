from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Optional

class GastoCreate(BaseModel):
    fecha: Optional[date] = None
    concepto: str
    valor: Decimal
    id_proveedor: Optional[int] = None 
    proveedor: Optional[str] = None
    nota: Optional[str] = None
    tipo_pago: str = "contado"
    id_arqueo: Optional[int] = None
    
    # 🚀 CAMBIO QUIRÚRGICO:
    # Quítale el Optional y déjalo con un valor por defecto claro
    cantidad: int = 1