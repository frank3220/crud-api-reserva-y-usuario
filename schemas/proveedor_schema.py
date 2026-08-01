from pydantic import BaseModel
from typing import Optional

class ProveedorBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    nit: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    nit: Optional[str] = None
    activo: Optional[bool] = None

class ProveedorOut(ProveedorBase):
    id_proveedor: int
    activo: bool

    class Config:
        from_attributes = True
