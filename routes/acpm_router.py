# routes/acpm.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies.database import get_db
from services.acpm_service import AcpmService

from schemas.acpm import (
    ACPMCreate,
    ACPMOut,
    ACPMAbono,
    ACPMCreditoOut
)

router = APIRouter(prefix="/acpm", tags=["ACPM"])


# ============================================================
# 🟩 CREAR ACPM (Contado o Crédito)
# ============================================================
@router.post("/", response_model=ACPMOut)
def crear_acpm(data: ACPMCreate, db: Session = Depends(get_db)):
    svc = AcpmService(db)
    return svc.registrar(data)


# ============================================================
# 🟩 LISTAR TODOS LOS REGISTROS ACPM
# ============================================================
@router.get("/", response_model=list[ACPMOut])
def obtener_acpm(db: Session = Depends(get_db)):
    svc = AcpmService(db)
    return svc.listar()


# ============================================================
# 🟩 ELIMINAR REGISTRO ACPM
# ============================================================
@router.delete("/{id_acpm}")
def eliminar_acpm(id_acpm: int, db: Session = Depends(get_db)):
    svc = AcpmService(db)
    ok = svc.eliminar(id_acpm)

    if not ok:
        raise HTTPException(404, "Registro ACPM no encontrado")

    return {"status": "ok"}


# ============================================================
# 🟩 LISTAR CRÉDITOS PENDIENTES
# ============================================================
@router.get("/pendientes", response_model=list[ACPMCreditoOut])
def acpm_creditos_pendientes(db: Session = Depends(get_db)):
    svc = AcpmService(db)
    return svc.listar_creditos_pendientes()


# ============================================================
# 🟩 ABONAR A UN ACPM A CRÉDITO
# ============================================================
@router.post("/abonar/{id_acpm}", response_model=ACPMOut)
def abonar_acpm(id_acpm: int, data: ACPMAbono, db: Session = Depends(get_db)):
    svc = AcpmService(db)
    result = svc.abonar_credito(id_acpm, data.monto)

    if result is None:
        raise HTTPException(404, "Registro ACPM no encontrado")

    return result


# ============================================================
# 🟩 PAGAR COMPLETO UN CRÉDITO ACPM
# ============================================================
@router.post("/pagar/{id_acpm}", response_model=ACPMOut)
def pagar_acpm(id_acpm: int, db: Session = Depends(get_db)):
    svc = AcpmService(db)
    result = svc.pagar_credito(id_acpm)

    if result is None:
        raise HTTPException(404, "Registro ACPM no encontrado")

    return result
