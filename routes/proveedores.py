from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.proveedor_service import ProveedorService
from schemas.proveedor_schema import (
    ProveedorCreate,
    ProveedorUpdate,
    ProveedorOut
)

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.get("/", response_model=list[ProveedorOut])
def listar(db: Session = Depends(get_db)):
    return ProveedorService(db).listar()

@router.post("/", response_model=ProveedorOut)
def crear(data: ProveedorCreate, db: Session = Depends(get_db)):
    return ProveedorService(db).crear(data)

@router.put("/{id_proveedor}", response_model=ProveedorOut)
def actualizar(id_proveedor: int, data: ProveedorUpdate, db: Session = Depends(get_db)):
    proveedor = ProveedorService(db).actualizar(id_proveedor, data)
    if not proveedor:
        raise HTTPException(404, "Proveedor no encontrado")
    return proveedor

@router.patch("/{id_proveedor}/estado", response_model=ProveedorOut)
def cambiar_estado(id_proveedor: int, db: Session = Depends(get_db)):
    proveedor = ProveedorService(db).toggle_activo(id_proveedor)
    if not proveedor:
        raise HTTPException(404, "Proveedor no encontrado")
    return proveedor
