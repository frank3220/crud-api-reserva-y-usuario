from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from dependencies.database import get_db
from services.arqueo import ArqueoService
# 🔥 IMPORTANTE: Traemos la seguridad para identificar al cajero
from utils.security import get_current_user, RoleChecker

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard / Arqueo"]
)

# ============================================================
# ✅ CAJA → RESUMEN DEL TURNO ACTIVO
# GET /dashboard/arqueo-turno
# ============================================================
@router.get("/arqueo-turno")
def arqueo_turno_activo(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # 🔒 Identifica al cajero logueado
):
    service = ArqueoService(db)
    # Le pasamos el ID del usuario al servicio
    return service.resumen_turno_activo(usuario_id=current_user.idusuario)


# ============================================================
# 📊 REPORTES → RESUMEN POR DÍA (🔒 Solo ADMIN)
# GET /dashboard/arqueo-dia?fecha=YYYY-MM-DD
# ============================================================
@router.get("/arqueo-dia")
def arqueo_dia(
    fecha: date = date.today(),
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["ADMIN"])) # 🔒 Solo el jefe ve reportes por día
):
    service = ArqueoService(db)
    return service.resumen_dia(fecha)


# ============================================================
# 🔥 CERRAR TURNO
# POST /dashboard/arqueo/cerrar-turno
# ============================================================
@router.post("/arqueo/cerrar-turno")
def cerrar_turno(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # 🔒 Solo el dueño del turno cierra su caja
):
    service = ArqueoService(db)
    # Le pasamos el ID del usuario para cerrar SU arqueo
    return service.cerrar_turno(usuario_id=current_user.idusuario)
# AGREGA ESTA RUTA PARA LA RE-IMPRESIÓN
@router.get("/arqueos/detalle/{id_arqueo}")
def obtener_detalle_reimpresion(id_arqueo: int, db: Session = Depends(get_db)):
    service = ArqueoService(db)
    resultado = service.obtener_detalle_arqueo(id_arqueo)
    if not resultado:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Arqueo no encontrado")
    return resultado