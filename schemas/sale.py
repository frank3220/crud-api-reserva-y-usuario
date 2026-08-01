from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Importamos el esquema de Habitación para poder incluirlo en la respuesta
# Esto permite que SaleOut muestre la info de la habitación asociada
from schemas.room import RoomOut 

# ------------------------------------------------
# BASE: Campos comunes para lectura y escritura
# ------------------------------------------------
class SaleBase(BaseModel):
    id_habitacion: int = Field(..., description="ID de la habitación ocupada")
    fecha_entrada: datetime = Field(..., description="Marca de tiempo de entrada/inicio de la venta")
    estado: str = Field("ACTIVA", max_length=50, description="Estado de la venta (ACTIVA, FINALIZADA, CANCELADA)")
    
    # Estos campos son opcionales y se llenan al momento de finalizar la venta
    fecha_salida: Optional[datetime] = Field(None, description="Marca de tiempo de salida/final de la venta")
    monto_total: Optional[float] = Field(None, ge=0, description="Costo total calculado de la estancia")
    
    # Estos campos son internos y se usan para el registro (se pueden omitir en la entrada)
    usuario_registro: Optional[str] = Field(None, max_length=50, description="Usuario que registra la venta")
    notas: Optional[str] = Field(None, description="Notas o comentarios de la venta")

# ------------------------------------------------
# CREATE: Usado para crear una nueva venta (al ocupar la habitación)
# ------------------------------------------------
class SaleCreate(SaleBase):
    # En la creación, solo necesitamos la habitación y la hora de entrada
    fecha_entrada: datetime 
    id_habitacion: int

# ------------------------------------------------
# UPDATE: Esquema usado para actualizar la venta (CLAVE, esto era lo que faltaba)
# ------------------------------------------------
class SaleUpdate(BaseModel):
    # Usado internamente para actualizar la salida, monto y estado
    fecha_salida: Optional[datetime] = None
    monto_total: Optional[float] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

# ------------------------------------------------
# OUT: Esquema de salida/respuesta completa
# ------------------------------------------------
class SaleOut(SaleBase):
    id_venta: int = Field(..., description="ID interno de la venta (clave primaria)")
    
    # Agregamos la información completa de la habitación
    habitacion: RoomOut
    
    class Config:
        # Permite que el modelo se inicialice desde atributos de objeto (SQLAlchemy)
        from_attributes = True
