from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies.database import get_db
from services.ocupacion import OcupacionService
from schemas.ocupacion import OcupacionCreate, OcupacionResponse, OcupacionUpdate

router = APIRouter(prefix="/ocupaciones", tags=["Ocupaciones"])

def get_service(db: Session = Depends(get_db)):
    return OcupacionService(db)

# ------------------------------------------------------
# 1. INICIAR OCUPACIÓN (CHECK-IN)
# ------------------------------------------------------
@router.post("/iniciar", response_model=OcupacionResponse)
def iniciar_ocupacion(
    data: OcupacionCreate,
    service: OcupacionService = Depends(get_service)
):
    return service.crear_ocupacion(data, data.usuario_id)

# ------------------------------------------------------
# 2. CERRAR / FACTURAR (CHECK-OUT)
# ------------------------------------------------------
@router.patch("/cerrar/{ocupacion_id}", response_model=OcupacionResponse)
def cerrar_ocupacion(
    ocupacion_id: int,
    data: OcupacionUpdate,
    service: OcupacionService = Depends(get_service),
):
    return service.cerrar_ocupacion(ocupacion_id, data)

# ------------------------------------------------------
# 3. ANULAR OCUPACIÓN
# ------------------------------------------------------
@router.patch("/anular/{ocupacion_id}")
def anular_ocupacion(
    ocupacion_id: int,
    id_cajero: int, 
    service: OcupacionService = Depends(get_service),
):
    return service.anular_ocupacion(ocupacion_id, id_cajero)

# ------------------------------------------------------
# 4. OCUPACIONES ACTIVAS
# ------------------------------------------------------
@router.get("/activas", response_model=list[OcupacionResponse])
def ocupaciones_activas(service: OcupacionService = Depends(get_service)):
    return service.ocupaciones_activas()

# ------------------------------------------------------
# 5. HISTORIAL SIMPLE
# ------------------------------------------------------
@router.get("/historial", response_model=list[OcupacionResponse])
def historial(service: OcupacionService = Depends(get_service)):
    return service.historial()

# ------------------------------------------------------
# 6. REPORTE DE AUDITORÍA DETALLADO (NOMBRES DE USUARIOS)
# ------------------------------------------------------
# ✅ ESTO ES LO QUE FALTABA: Para la tabla de mamá
@router.get("/reporte/auditoria")
def reporte_auditoria(service: OcupacionService = Depends(get_service)):
    return service.obtener_reporte_auditoria()

# ------------------------------------------------------
# 7. TICKET DE REIMPRESIÓN
# ------------------------------------------------------
@router.get("/{ocupacion_id}")
def obtener_ocupacion_por_id(
    ocupacion_id: int,
    service: OcupacionService = Depends(get_service),
):
    return service.obtener_ocupacion_para_ticket(ocupacion_id)



# ------------------------------------------------------
# VENTAS FILTRADAS DEL TURNO PARA EL DASHBOARD
# ------------------------------------------------------
@router.get("/ventas-turno/{usuario_id}")
def obtener_ventas_del_turno(
    usuario_id: int, 
    service: OcupacionService = Depends(get_service)
):
    return service.obtener_ventas_turno_actual(usuario_id)