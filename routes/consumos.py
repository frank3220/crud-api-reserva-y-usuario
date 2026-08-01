# routes/consumos.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.database import get_db
from services.consumo_service import ConsumoService
from schemas.consumo_schema import ConsumoCreate
from datetime import datetime
from models.consumo import Consumo

router = APIRouter(prefix="/consumos", tags=["Consumos"])

@router.post("/", summary="Registrar consumo")
def crear_consumo(data: ConsumoCreate, db: Session = Depends(get_db)):
    svc = ConsumoService(db)
    return svc.crear(data)

@router.get("/dia", summary="Consumos del día")
def listar_consumos_dia(fecha: str, db: Session = Depends(get_db)):
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    svc = ConsumoService(db)
    return svc.listar_dia(fecha_obj)

@router.get("/pendientes", summary="Consumos sin arqueo")
def pendientes(db: Session = Depends(get_db)):
    svc = ConsumoService(db)
    return svc.listar_pendientes()

@router.post("/asignar-arqueo/{id_arqueo}", summary="Asignar consumos a arqueo")
def asignar_consumos(id_arqueo: int, db: Session = Depends(get_db)):
    svc = ConsumoService(db)
    return svc.asignar_a_arqueo(id_arqueo)

@router.get("/ocupacion/{id_ocupacion}", summary="Consumos por ocupación")
def consumos_por_ocupacion(id_ocupacion: int, db: Session = Depends(get_db)):
    svc = ConsumoService(db)
    return svc.listar_por_ocupacion(id_ocupacion)

@router.delete("/{id_consumo}", summary="Eliminar consumo")
def eliminar_consumo(id_consumo: int, db: Session = Depends(get_db)):
    svc = ConsumoService(db)
    return svc.eliminar(id_consumo)

@router.get("/patio")
def listar_consumos_patio(db: Session = Depends(get_db)):
    return (
        db.query(Consumo)
        .filter(Consumo.id_ocupacion == None)
        .order_by(Consumo.id_consumo.desc())
        .all()
    )
