from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.arqueo_actual_service import ArqueoActualService

router = APIRouter(prefix="/arqueo-actual", tags=["Arqueo Actual"])

# ---------------------------------------------------
# Obtener el arqueo actual
# ---------------------------------------------------
@router.get("/")
def get_arqueo_actual(db: Session = Depends(get_db)):
    service = ArqueoActualService(db)
    return service.get_actual()

# ---------------------------------------------------
# Cerrar turno
# ---------------------------------------------------
@router.post("/cerrar")
def cerrar_turno(db: Session = Depends(get_db)):
    service = ArqueoActualService(db)
    return service.cerrar_turno()
