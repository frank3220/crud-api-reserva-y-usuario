from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.producto_service import ProductoService
from schemas.producto_schema import (
    ProductoCreate,
    ProductoUpdate,
    ProductoOut
)

router = APIRouter(prefix="/productos", tags=["Productos"])

# 🔹 listar productos activos
@router.get("/", response_model=list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    return ProductoService(db).listar()

# 🔹 crear producto
@router.post("/", response_model=ProductoOut)
def crear_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    return ProductoService(db).crear(data)

# ✏️ editar producto
@router.put("/{id_producto}", response_model=ProductoOut)
def actualizar_producto(
    id_producto: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db)
):
    producto = ProductoService(db).actualizar(id_producto, data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# 🟢🔴 activar / desactivar
@router.patch("/{id_producto}/estado", response_model=ProductoOut)
def cambiar_estado_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):
    producto = ProductoService(db).cambiar_estado(id_producto)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# ============================================================
# 🆕 INVENTARIO GENERAL (para Patio / Consumos)
# ============================================================
@router.get("/inventario", summary="Inventario general de productos")
def inventario_productos(db: Session = Depends(get_db)):
    """
    Devuelve TODOS los productos con su stock actual.
    Usado para mostrar inventario en Consumo Patio.
    """
    return ProductoService(db).listar_inventario()
