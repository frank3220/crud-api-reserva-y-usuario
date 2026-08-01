from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str
    precio: float

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id_producto: int
    activo: bool

    class Config:
        from_attributes = True
